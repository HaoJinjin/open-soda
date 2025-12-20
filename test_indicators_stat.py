"""
测试 indicators_stat.py 的修改
验证：
1. projects_detail 字段是否正确添加
2. Top10 标准化值是否在 0-1 范围内（不再是负数）
3. 数据结构是否完整
"""

import json

print("=" * 60)
print("🧪 测试 indicators_stat.py 修改")
print("=" * 60)

# 读取生成的 JSON 文件
json_path = r'C:\Users\22390\Desktop\OpenSODA\backendData\indicators_stat.json'

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    print("\n✅ JSON 文件加载成功")
    
    # 测试 1: 检查 projects_detail 字段
    print("\n" + "=" * 60)
    print("测试 1: 检查 projects_detail 字段")
    print("=" * 60)
    
    if 'projects_detail' in result:
        print(f"✅ projects_detail 字段存在")
        print(f"   项目数量: {len(result['projects_detail'])}")
        
        # 检查第一个项目的数据结构
        if len(result['projects_detail']) > 0:
            first_project = result['projects_detail'][0]
            print(f"\n   第一个项目示例:")
            print(f"   - project_index: {first_project.get('project_index')}")
            print(f"   - project_name: {first_project.get('project_name')}")
            print(f"   - inactive_contributors: {first_project.get('inactive_contributors')}")
            print(f"   - issues_new: {first_project.get('issues_new')}")
            print(f"   - participants: {first_project.get('participants')}")
            
            # 检查是否包含所有 6 个指标
            expected_indicators = [
                'inactive_contributors',
                'issues_and_change_request_active',
                'issues_closed',
                'issues_new',
                'new_contributors',
                'participants'
            ]
            missing_indicators = [ind for ind in expected_indicators if ind not in first_project]
            if missing_indicators:
                print(f"   ❌ 缺少指标: {missing_indicators}")
            else:
                print(f"   ✅ 包含所有 6 个指标")
    else:
        print(f"❌ projects_detail 字段不存在")
    
    # 测试 2: 检查 Top10 标准化值
    print("\n" + "=" * 60)
    print("测试 2: 检查 Top10 标准化值（应该在 0-1 范围内）")
    print("=" * 60)
    
    if 'top10_projects' in result and len(result['top10_projects']) > 0:
        print(f"✅ top10_projects 字段存在，共 {len(result['top10_projects'])} 个项目")
        
        # 检查所有标准化值
        all_scaled_values = []
        has_negative = False
        has_out_of_range = False
        
        for project in result['top10_projects']:
            for key, value in project['indicator_values'].items():
                if key.endswith('_scaled'):
                    all_scaled_values.append(value)
                    if value < 0:
                        has_negative = True
                        print(f"   ❌ 发现负数: {project['project_name']} - {key} = {value}")
                    if value < 0 or value > 1:
                        has_out_of_range = True
        
        if not has_negative:
            print(f"   ✅ 没有负数标准化值")
        
        if not has_out_of_range:
            print(f"   ✅ 所有标准化值都在 0-1 范围内")
        
        print(f"\n   标准化值统计:")
        print(f"   - 最小值: {min(all_scaled_values):.4f}")
        print(f"   - 最大值: {max(all_scaled_values):.4f}")
        print(f"   - 平均值: {sum(all_scaled_values) / len(all_scaled_values):.4f}")
        
        # 显示第一个项目的标准化值
        first_project = result['top10_projects'][0]
        print(f"\n   第一个项目 ({first_project['project_name']}) 的标准化值:")
        for key, value in first_project['indicator_values'].items():
            if key.endswith('_scaled'):
                print(f"   - {key}: {value}")
    else:
        print(f"❌ top10_projects 字段不存在或为空")
    
    # 测试 3: 检查数据结构完整性
    print("\n" + "=" * 60)
    print("测试 3: 检查数据结构完整性")
    print("=" * 60)
    
    required_fields = ['metadata', 'projects_detail', 'indicator_statistics', 'correlation_matrix', 'top10_projects']
    for field in required_fields:
        if field in result:
            print(f"   ✅ {field} 存在")
        else:
            print(f"   ❌ {field} 缺失")
    
    # 测试 4: 数据量对比
    print("\n" + "=" * 60)
    print("测试 4: 数据量对比（验证优化效果）")
    print("=" * 60)
    
    # 计算如果使用旧方案（每个指标都存储 detail_data）的数据量
    projects_count = len(result.get('projects_detail', []))
    indicators_count = len(result.get('indicator_statistics', []))
    
    old_approach_records = projects_count * indicators_count  # 旧方案：重复 6 次
    new_approach_records = projects_count  # 新方案：只存储 1 次
    
    print(f"   旧方案（重复存储）: {old_approach_records} 条记录")
    print(f"   新方案（顶层共用）: {new_approach_records} 条记录")
    print(f"   节省空间: {((old_approach_records - new_approach_records) / old_approach_records * 100):.1f}%")
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("=" * 60)

except FileNotFoundError:
    print(f"\n❌ 文件不存在: {json_path}")
    print("   请先运行 backend/indicators_stat.py 生成 JSON 文件")
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

