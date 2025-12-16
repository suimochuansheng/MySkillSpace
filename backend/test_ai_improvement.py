#!/usr/bin/env python
"""
AI内容量优化效果测试脚本
用于验证修改后的AI回复长度和质量

使用方法：
  cd e:\skillSpace\backend
  .\sk_venv\Scripts\Activate.ps1
  python test_ai_improvement.py
"""

import os
import sys
import django

# 配置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillSpace.settings')
django.setup()

from myapps.ai_demo.model_loader import stream_generate_answer

# 测试提示词集合（从简到复杂）
TEST_PROMPTS = [
    # 简单问题
    "什么是Python装饰器？",
    
    # 中等问题
    "请详细解释Python装饰器的实现原理和常见应用场景",
    
    # 复杂问题
    "请详细介绍Python的装饰器模式，包括实现原理、常见用途、最佳实践和性能考虑。举个复杂的例子。",
]

def test_ai_response(prompt, test_num=1):
    """测试单个AI回复"""
    print(f"\n{'='*80}")
    print(f"测试 #{test_num}: {prompt[:60]}...")
    print(f"{'='*80}")
    
    full_response = ""
    token_count = 0
    chunk_count = 0
    
    try:
        for chunk in stream_generate_answer(prompt):
            token = chunk.get("token", "")
            chunk_type = chunk.get("type", "")
            
            if chunk_type == "answer":
                full_response += token
                token_count += 1
                chunk_count += 1
            elif chunk_type == "finish":
                print(f"\n✅ AI回复已完成")
                break
            elif chunk_type == "error":
                print(f"❌ 错误: {token}")
                return None
        
        # 统计信息
        char_count = len(full_response)
        word_count = len(full_response.split())
        
        print(f"\n📊 统计信息:")
        print(f"  • 字符数: {char_count}")
        print(f"  • 中文字数（估算）: {int(char_count * 0.6)}")  # 中文通常占60%
        print(f"  • Token数: {token_count}")
        print(f"  • 词数: {word_count}")
        print(f"  • 平均Token长度: {char_count/token_count:.1f} 字符/token" if token_count > 0 else "")
        
        print(f"\n📝 回复内容（前500字）:")
        print("-" * 80)
        print(full_response[:500])
        if len(full_response) > 500:
            print(f"... （省略，共{char_count}字）")
        print("-" * 80)
        
        return {
            "prompt": prompt,
            "response": full_response,
            "char_count": char_count,
            "token_count": token_count,
            "word_count": word_count
        }
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主测试流程"""
    print("\n🚀 AI内容量优化效果测试")
    print("=" * 80)
    print("本脚本测试以下优化项：")
    print("  ✅ max_new_tokens: 2048 → 4096")
    print("  ✅ temperature: 0.7 → 0.8")
    print("  ✅ top_p: 0.8 → 0.9")
    print("  ✅ top_k: 40 → 50")
    print("  ✅ System Prompt: 移除强制XML格式")
    print("  ✅ 流式处理: 简化XML解析")
    print("=" * 80)
    
    results = []
    
    # 运行所有测试
    for idx, prompt in enumerate(TEST_PROMPTS, 1):
        result = test_ai_response(prompt, test_num=idx)
        if result:
            results.append(result)
        # 测试间隔，避免显存溢出
        if idx < len(TEST_PROMPTS):
            input("\n按 Enter 继续下一个测试...")
    
    # 总结报告
    if results:
        print("\n" + "=" * 80)
        print("📊 测试总结报告")
        print("=" * 80)
        
        total_chars = sum(r["char_count"] for r in results)
        total_tokens = sum(r["token_count"] for r in results)
        avg_chars = total_chars / len(results) if results else 0
        
        print(f"\n测试数量: {len(results)}")
        print(f"总字符数: {total_chars}")
        print(f"总Token数: {total_tokens}")
        print(f"平均回复字符数: {avg_chars:.0f}")
        print(f"平均Token数: {total_tokens/len(results):.0f}")
        
        print(f"\n✅ 优化目标检查:")
        if avg_chars > 1000:
            print(f"  ✅ 内容量充足（>1000字）: 实际 {avg_chars:.0f} 字")
        else:
            print(f"  ⚠️  内容量偏少（<1000字）: 实际 {avg_chars:.0f} 字")
        
        if all(r["char_count"] > 500 for r in results):
            print(f"  ✅ 每个回复都>500字")
        else:
            print(f"  ⚠️  有回复<500字")
        
        # 检查回复完整性
        incomplete = [r for r in results if not r["response"].strip().endswith('。')]
        if not incomplete:
            print(f"  ✅ 所有回复完整性良好（以。结尾）")
        else:
            print(f"  ⚠️  {len(incomplete)}个回复可能被截断")
        
        print("\n💡 建议:")
        if avg_chars > 1500:
            print("  ✅ 优化效果显著，内容量已明显提升")
        elif avg_chars > 1000:
            print("  ✅ 优化效果良好，内容量已改善")
        else:
            print("  ⚠️  内容量仍需改进，可考虑：")
            print("     - 进一步增加 max_new_tokens")
            print("     - 检查模型是否正确加载")
            print("     - 检查GPU显存是否充足")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  测试已中止")
    except Exception as e:
        print(f"\n❌ 测试脚本错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
