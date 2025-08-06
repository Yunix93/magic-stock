"""
运行所有测试

统一的测试运行器，执行所有测试模块
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有测试类
from test_user_model import TestUserModel
from test_role_model import TestRoleModel
from test_permission_model import TestPermissionModel
from test_user_service import TestUserService
from test_role_service import TestRoleService
from test_permission_service import TestPermissionService
from test_integration import TestIntegration


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试")
    print("=" * 60)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 定义所有测试类
    test_classes = [
        ("用户模型测试", TestUserModel),
        ("角色模型测试", TestRoleModel),
        ("权限模型测试", TestPermissionModel),
        ("用户服务测试", TestUserService),
        ("角色服务测试", TestRoleService),
        ("权限服务测试", TestPermissionService),
        ("集成测试", TestIntegration)
    ]
    
    # 运行测试统计
    total_test_suites = len(test_classes)
    passed_test_suites = 0
    failed_test_suites = []
    
    # 运行每个测试类
    for test_name, test_class in test_classes:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            test_instance = test_class()
            success = test_instance.run_all_tests()
            
            if success:
                passed_test_suites += 1
                print(f"✅ {test_name} 全部通过")
            else:
                failed_test_suites.append(test_name)
                print(f"❌ {test_name} 部分失败")
                
        except Exception as e:
            failed_test_suites.append(test_name)
            print(f"❌ {test_name} 执行异常: {e}")
    
    # 打印总体结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    print(f"总测试套件数: {total_test_suites}")
    print(f"通过测试套件: {passed_test_suites}")
    print(f"失败测试套件: {len(failed_test_suites)}")
    
    if failed_test_suites:
        print(f"\n❌ 失败的测试套件:")
        for failed_suite in failed_test_suites:
            print(f"  - {failed_suite}")
    
    # 计算成功率
    success_rate = (passed_test_suites / total_test_suites) * 100
    print(f"\n📈 测试成功率: {success_rate:.1f}%")
    
    print(f"\n⏰ 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed_test_suites == total_test_suites:
        print("\n🎉 所有测试套件都通过了！")
        return True
    else:
        print(f"\n⚠️ 有 {len(failed_test_suites)} 个测试套件失败")
        return False


def run_specific_test(test_name):
    """运行特定的测试"""
    test_mapping = {
        'user_model': TestUserModel,
        'role_model': TestRoleModel,
        'permission_model': TestPermissionModel,
        'user_service': TestUserService,
        'role_service': TestRoleService,
        'permission_service': TestPermissionService,
        'integration': TestIntegration
    }
    
    if test_name not in test_mapping:
        print(f"❌ 未找到测试: {test_name}")
        print(f"可用的测试: {', '.join(test_mapping.keys())}")
        return False
    
    test_class = test_mapping[test_name]
    print(f"🧪 运行测试: {test_name}")
    
    try:
        test_instance = test_class()
        return test_instance.run_all_tests()
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 运行特定测试
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # 运行所有测试
        success = run_all_tests()
    
    # 设置退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()