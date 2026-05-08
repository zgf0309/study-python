# 中文注释：导入当前脚本需要使用的模块。
import json
# 中文注释：从业务模块导入需要验证的函数。
from app.routes.users import read_users

# 中文注释：定义验证函数，用于检查用户列表接口行为。
def test_read_users():
    # Test page=1
    # 中文注释：设置变量值，保存接口响应或验证结果。
    response1 = read_users(page=1)
    # 中文注释：设置变量值，保存接口响应或验证结果。
    body1 = json.loads(response1.body)
    # 中文注释：打印验证结果或调试信息。
    print(f"Page 1 response: {body1}")
    # 中文注释：设置变量值，保存接口响应或验证结果。
    has_total1 = 'total' in body1
    
    # Test page=2
    # 中文注释：设置变量值，保存接口响应或验证结果。
    response2 = read_users(page=2)
    # 中文注释：设置变量值，保存接口响应或验证结果。
    body2 = json.loads(response2.body)
    # 中文注释：打印验证结果或调试信息。
    print(f"Page 2 response: {body2}")
    # 中文注释：设置变量值，保存接口响应或验证结果。
    has_total2 = 'total' in body2
    
    # 中文注释：打印验证结果或调试信息。
    print(f"Page 1 has total: {has_total1}")
    # 中文注释：打印验证结果或调试信息。
    print(f"Page 2 has total: {has_total2}")
    
    # 中文注释：判断条件是否成立，并执行对应分支。
    if not has_total1 and has_total2:
        # 中文注释：打印验证结果或调试信息。
        print("Verification SUCCESS: Page 1 does NOT have total, Page 2 HAS total.")
    # 中文注释：当前面条件不成立时，执行失败分支。
    else:
        # 中文注释：打印验证结果或调试信息。
        print("Verification FAILED.")

# 中文注释：判断条件是否成立，并执行对应分支。
if __name__ == "__main__":
    # 中文注释：开始执行可能抛出异常的验证逻辑。
    try:
        # 中文注释：调用函数，执行对应验证步骤。
        test_read_users()
    # 中文注释：捕获异常并打印调试信息。
    except Exception as e:
        # 中文注释：导入当前脚本需要使用的模块。
        import traceback
        # 中文注释：调用函数，执行对应验证步骤。
        traceback.print_exc()
