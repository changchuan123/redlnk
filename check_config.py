#!/usr/bin/env python3
"""
配置验证脚本 - 用于检查配置是否正确
"""
import yaml
import sys
import os

def check_text_providers_config():
    """检查文本生成服务配置"""
    try:
        config_path = 'text_providers.yaml'
        if not os.path.exists(config_path):
            print(f"❌ 配置文件不存在: {config_path}")
            return False

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print("✅ 配置文件格式正确")

        active_provider = config.get('active_provider')
        print(f"激活的服务商: {active_provider}")

        providers = config.get('providers', {})
        deepseek_config = providers.get('deepseek', {})
        gemini_config = providers.get('gemini', {})

        # 检查 DeepSeek 配置
        print(f"\n📋 DeepSeek 配置:")
        print(f"  API Key: {'已配置' if deepseek_config.get('api_key') else '❌ 未配置'}")
        print(f"  Base URL: {deepseek_config.get('base_url')}")
        print(f"  Model: {deepseek_config.get('model')}")
        print(f"  Endpoint: {deepseek_config.get('endpoint_type')}")

        # 检查 Gemini 配置
        print(f"\n📋 Gemini 配置:")
        print(f"  API Key: {'已配置' if gemini_config.get('api_key') else '❌ 未配置'}")
        print(f"  Base URL: {gemini_config.get('base_url')}")
        print(f"  Model: {gemini_config.get('model')}")

        # 验证 DeepSeek URL 生成
        base_url = deepseek_config.get('base_url', '').rstrip('/').rstrip('/v1')
        endpoint = deepseek_config.get('endpoint_type', '/v1/chat/completions')
        final_url = f"{base_url}{endpoint}"
        print(f"\n🔗 DeepSeek 最终端点: {final_url}")

        # 检查 URL 是否正确
        if final_url == "https://api.deepseek.com/v1/chat/completions":
            print("✅ DeepSeek 端点配置正确")
        else:
            print(f"❌ DeepSeek 端点配置错误，期望: https://api.deepseek.com/v1/chat/completions")
            return False

        return True

    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 开始检查配置文件...")
    success = check_text_providers_config()
    sys.exit(0 if success else 1)