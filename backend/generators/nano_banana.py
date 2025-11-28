"""Nano Banana 图片生成器（异步任务模式）"""
import logging
import time
import requests
from typing import Dict, Any, Optional, List
from .base import ImageGeneratorBase
from ..utils.image_compressor import compress_image
import base64

logger = logging.getLogger(__name__)


class NanoBananaGenerator(ImageGeneratorBase):
    """Nano Banana 图片生成器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        logger.debug("初始化 NanoBananaGenerator...")
        self.base_url = config.get('base_url', 'https://grsai.dakka.com.cn').rstrip('/')
        self.model = config.get('model', 'nano-banana-fast')
        self.default_aspect_ratio = config.get('default_aspect_ratio', '3:4')
        self.max_poll_attempts = config.get('max_poll_attempts', 60)  # 最多轮询60次
        self.poll_interval = config.get('poll_interval', 2)  # 每2秒轮询一次
        logger.info(f"NanoBananaGenerator 初始化完成: base_url={self.base_url}, model={self.model}")

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.api_key:
            logger.error("Nano Banana API Key 未配置")
            raise ValueError(
                "Nano Banana API Key 未配置。\n"
                "解决方案：在系统设置页面编辑该服务商，填写 API Key"
            )
        return True

    def get_supported_sizes(self) -> List[str]:
        """获取支持的图片尺寸"""
        return ["1K", "2K", "4K"]

    def get_supported_aspect_ratios(self) -> List[str]:
        """获取支持的宽高比"""
        return ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"]

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = None,
        temperature: float = 1.0,
        model: str = None,
        reference_image: Optional[bytes] = None,
        reference_images: Optional[List[bytes]] = None,
        **kwargs
    ) -> bytes:
        """
        生成图片（异步任务模式）

        Args:
            prompt: 图片描述
            aspect_ratio: 宽高比
            temperature: 创意度（未使用，保留接口兼容）
            model: 模型名称
            reference_image: 单张参考图片数据（向后兼容）
            reference_images: 多张参考图片数据列表

        Returns:
            生成的图片二进制数据
        """
        self.validate_config()

        if aspect_ratio is None:
            aspect_ratio = self.default_aspect_ratio

        if model is None:
            model = self.model

        logger.info(f"Nano Banana 生成图片: model={model}, aspect_ratio={aspect_ratio}")

        # 1. 提交任务
        task_id = self._submit_task(prompt, aspect_ratio, model, reference_image, reference_images)

        # 2. 轮询任务状态
        image_data = self._poll_task_result(task_id)

        logger.info(f"✅ Nano Banana 图片生成成功: {len(image_data)} bytes")
        return image_data

    def _submit_task(
        self,
        prompt: str,
        aspect_ratio: str,
        model: str,
        reference_image: Optional[bytes] = None,
        reference_images: Optional[List[bytes]] = None
    ) -> str:
        """提交图片生成任务"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "urls": [],
            "webHook": "",
            "shutProgress": False
        }

        # 处理参考图片
        all_reference_images = []
        if reference_images and len(reference_images) > 0:
            all_reference_images.extend(reference_images)
        if reference_image and reference_image not in all_reference_images:
            all_reference_images.append(reference_image)

        if all_reference_images:
            logger.debug(f"  添加 {len(all_reference_images)} 张参考图片")
            # Nano Banana API 支持通过 URLs 传递参考图片
            # 这里我们需要将图片转换为 base64 或上传到临时存储
            # 暂时先不处理参考图片，后续可以扩展
            logger.warning("Nano Banana API 参考图片功能暂未实现，将忽略参考图片")

        api_url = f"{self.base_url}/v1/draw/nano-banana"
        logger.debug(f"  提交任务到: {api_url}")

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code != 200:
                error_detail = response.text[:500]
                logger.error(f"Nano Banana 提交任务失败: status={response.status_code}, error={error_detail}")
                raise Exception(
                    f"Nano Banana 提交任务失败 (状态码: {response.status_code})\n"
                    f"错误详情: {error_detail}\n"
                    f"请求地址: {api_url}\n"
                    "可能原因：\n"
                    "1. API密钥无效或已过期\n"
                    "2. 请求参数不符合API要求\n"
                    "3. API服务端错误\n"
                    "建议：检查API密钥和配置"
                )

            result = response.json()
            logger.debug(f"  任务提交响应: {result}")

            # 提取任务ID
            if "id" in result:
                task_id = result["id"]
                logger.info(f"✅ 任务提交成功，任务ID: {task_id}")
                return task_id
            elif "task_id" in result:
                task_id = result["task_id"]
                logger.info(f"✅ 任务提交成功，任务ID: {task_id}")
                return task_id
            else:
                raise Exception(
                    f"无法从响应中提取任务ID\n"
                    f"API响应: {str(result)[:500]}\n"
                    "可能原因：API返回格式与预期不符"
                )

        except requests.exceptions.Timeout:
            raise Exception("❌ 提交任务超时，请重试")
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ 提交任务失败: {str(e)}")

    def _poll_task_result(self, task_id: str) -> bytes:
        """轮询任务结果"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        api_url = f"{self.base_url}/v1/draw/result"
        logger.info(f"开始轮询任务结果: task_id={task_id}")

        for attempt in range(self.max_poll_attempts):
            try:
                payload = {"id": task_id}
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code != 200:
                    error_detail = response.text[:500]
                    logger.warning(f"查询任务状态失败 (尝试 {attempt + 1}/{self.max_poll_attempts}): status={response.status_code}, error={error_detail}")
                    if attempt < self.max_poll_attempts - 1:
                        time.sleep(self.poll_interval)
                        continue
                    else:
                        raise Exception(
                            f"查询任务状态失败 (状态码: {response.status_code})\n"
                            f"错误详情: {error_detail}"
                        )

                result = response.json()
                logger.debug(f"  任务状态响应 (尝试 {attempt + 1}): {result}")

                # 检查任务状态
                status = result.get("status", "").lower()
                
                if status == "completed" or status == "success":
                    # 任务完成，提取图片
                    image_url = result.get("image_url") or result.get("url") or result.get("image")
                    if image_url:
                        logger.info(f"✅ 任务完成，下载图片: {image_url[:100]}...")
                        return self._download_image(image_url)
                    
                    # 尝试从 base64 数据提取
                    image_data = result.get("image_data") or result.get("data")
                    if image_data:
                        if isinstance(image_data, str):
                            if image_data.startswith("data:image"):
                                base64_data = image_data.split(",")[1]
                            else:
                                base64_data = image_data
                            logger.info("✅ 任务完成，从 base64 提取图片")
                            return base64.b64decode(base64_data)
                    
                    raise Exception(
                        "任务已完成但无法提取图片数据\n"
                        f"API响应: {str(result)[:500]}"
                    )
                
                elif status == "failed" or status == "error":
                    error_msg = result.get("error", result.get("message", "未知错误"))
                    raise Exception(f"任务失败: {error_msg}")
                
                elif status == "processing" or status == "pending" or status == "running":
                    # 任务进行中，继续轮询
                    progress = result.get("progress", 0)
                    logger.debug(f"  任务进行中 (进度: {progress}%), 等待 {self.poll_interval} 秒后重试...")
                    time.sleep(self.poll_interval)
                    continue
                
                else:
                    # 未知状态，继续轮询
                    logger.warning(f"  未知任务状态: {status}, 继续轮询...")
                    time.sleep(self.poll_interval)
                    continue

            except requests.exceptions.Timeout:
                logger.warning(f"查询任务状态超时 (尝试 {attempt + 1}/{self.max_poll_attempts})")
                if attempt < self.max_poll_attempts - 1:
                    time.sleep(self.poll_interval)
                    continue
                else:
                    raise Exception("❌ 查询任务状态超时，请重试")
            except Exception as e:
                if "任务失败" in str(e) or "无法提取图片" in str(e):
                    raise
                logger.warning(f"查询任务状态异常 (尝试 {attempt + 1}/{self.max_poll_attempts}): {str(e)}")
                if attempt < self.max_poll_attempts - 1:
                    time.sleep(self.poll_interval)
                    continue
                else:
                    raise Exception(f"❌ 查询任务状态失败: {str(e)}")

        # 超过最大轮询次数
        raise Exception(
            f"❌ 任务超时：已轮询 {self.max_poll_attempts} 次（约 {self.max_poll_attempts * self.poll_interval} 秒）\n"
            f"任务ID: {task_id}\n"
            "可能原因：\n"
            "1. 图片生成时间过长\n"
            "2. API服务异常\n"
            "建议：稍后重试或检查任务状态"
        )

    def _download_image(self, url: str) -> bytes:
        """下载图片并返回二进制数据"""
        logger.info(f"下载图片: {url[:100]}...")
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                logger.info(f"✅ 图片下载成功: {len(response.content)} bytes")
                return response.content
            else:
                raise Exception(f"下载图片失败: HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            raise Exception("❌ 下载图片超时，请重试")
        except Exception as e:
            raise Exception(f"❌ 下载图片失败: {str(e)}")

