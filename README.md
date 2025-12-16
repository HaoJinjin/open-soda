OpenSoda数据展示模块须知：
本项目是一个展示模块，用于展示OpenSoda数据，下面是单个数据的数据结构：（像这样的数据有300个）
 {
    "﻿projectname": "AUTOMATIC1111",
    "projectname2": "stable-diffusion-webui",
    "active_dates_and_times": "[3, 3, 3, 4, 3, 2, 4, 4, 4, 2, 3, 1, 6, 2, 2, 0, 1, 3, 2, 1, 1, 3, 2, 2, 2, 4, 6, 2, 3, 6, 2, 3, 1, 3, 1, 6, 1, 3, 2, 2, 1, 3, 2, 1, 6, 4, 10, 2, 2, 2, 1, 2, 1, 2, 3, 4, 4, 1, 1, 2, 1, 4, 5, 4, 1, 1, 2, 2, 3, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 2, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 4, 2, 1, 0, 0, 0, 1, 2, 0, 2, 2, 1, 0, 0, 1, 0, 0, 2, 0, 3, 1, 1, 0, 0, 1, 1, 0, 1, 2, 1, 2, 3, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 0, 4, 0, 2, 0, 0, 1, 3, 1, 2, 4, 2, 3, 1, 3, 5, 2, 2, 2, 2, 2]",
    "activity": "59.98",
    "activity_details": "[['1blackbar', 6.4], ['AUTOMATIC1111', 6.24], ['orionaskatu', 5.29], ['oobabooga', 3.16], ['Craftyawesome', 2.83], ['vasimr', 2.65], ['hlky', 2.24], ['cclauss', 2.24], ['dogewanwan', 2.24], ['raldnor', 2.24], ['UrielCh', 2], ['DustyWantingMicrowave', 2], ['jw-star', 1.73], ['LiJT', 1.73], ['Jpkovas', 1.73], ['ZeroCool22', 1.73], ['liangwei191', 1.73], ['caacoe', 1.73], ['bulleric', 1.41], ['pandoras-rabbithole', 1.41], ['DenkingOfficial', 1.41], ['lashmanRB', 1.41], ['SorraTheOrc', 1.41], ['krupalitrivedi', 1], ['khalidmarescalchi', 1], ['Pipazoul', 1]]",
    "attention": "531.0",
    "bus_factor": "10.0",
    "bus_factor_detail": "[['1blackbar', 7], ['dogewanwan', 3], ['cclauss', 3], ['raldnor', 3], ['Craftyawesome', 3], ['oobabooga', 4], ['vasimr', 3], ['AUTOMATIC1111', 7], ['orionaskatu', 6], ['hlky', 3]]",
    "change_requests": "12.0",
    "change_requests_accepted": "7.0",
    "change_requests_reviews": "26.0",
    "change_request_age": "{'2022-08': 1, '2022-09': 6.84, '2022-10': 13.69, '2022-11': 36.1, '2022-12': 58.13, '2023-01': 69.87, '2023-02': 72.6, '2023-03': 79.98}",
    "change_request_resolution_duration": "{'2022-08': 0.08, '2022-09': 3.49, '2022-10': 8.04, '2022-11': 12.28, '2022-12': 9.41, '2023-01': 2.07, '2023-02': 10.3, '2023-03': 3.71}",
    "change_request_response_time": "{'2022-08': 0, '2022-09': 1.83, '2022-10': 5.63, '2022-11': 7.79, '2022-12': 4.93, '2023-01': 2.33, '2023-02': 5.88, '2023-03': 2.25}",
    "code_change_lines_add": "3115.0",
    "code_change_lines_remove": "668.0",
    "code_change_lines_sum": "2447.0",
    "contributor_email_suffixes": "[['gmail.com', '3'], ['users.noreply.github.com', '3'], ['me.com', '1']]",
    "inactive_contributors": "4.0",
    "issues_and_change_request_active": "38.0",
    "issues_closed": "14.0",
    "issues_new": "26.0",
    "issue_age": "{'2022-08': 3.69, '2022-09': 9.83, '2022-10': 23.1, '2022-11': 44.06, '2022-12': 68.15, '2023-01': 77.01, '2023-02': 91.7, '2023-03': 105.49}",
    "issue_comments": "90.0",
    "issue_resolution_duration": "{'2022-08': 8.92, '2022-09': 19.8, '2022-10': 36.1, '2022-11': 29.15, '2022-12': 11.18, '2023-01': 3.34, '2023-02': 4.46, '2023-03': 2.35}",
    "issue_response_time": "{'2022-08': 6, '2022-09': 15.46, '2022-10': 29.73, '2022-11': 23.46, '2022-12': 17.62, '2023-01': 14.88, '2023-02': 11.93, '2023-03': 4.04}",
    "meta": "1680426181691.0",
    "new_contributors": "5.0",
    "new_contributors_detail": "['cclauss', 'hlky', 'Craftyawesome', 'orionaskatu', 'dogewanwan']",
    "openrank": "6.09",
    "participants": "26.0",
    "stars": "461.0",
    "technical_fork": "35.0"
  },

目前需要做的事展示统计这300行数据并展示出来，需要展示的有科技感又好看。
目前的src\components\layout\aside-layout.vue的配色需要进行修改，以迎合当前的科技风格需求，现在请你先配置好路由，创建好各个文件，然后生成一个全局总览给我看看效果，现在“全局总览”部分用的是src\components\showBorad.vue这个文件，请你直接在这上面进行替换

我目前分为了七大板块：
1. 全局总览（Overview）
用于展示项目的基本信息和核心指标

projectname（项目名称）
projectname2（项目别名）
activity（总体活跃度）
stars（星标数）
openrank（开放排名）
technical_fork（技术派生数量）
participants（参与者总数）
2. 活跃度分析（Activity Analysis）
分析项目的活跃程度和发展趋势

active_dates_and_times（活跃日期和时间分布）
activity（总体活跃度）
activity_details（活跃度详情，贡献者列表）
new_contributors（新贡献者数量）
inactive_contributors（不活跃贡献者数量）
3. 影响力分析（Impact Analysis）
评估项目在社区中的影响力

attention（关注度）
stars（星标数）
openrank（开放排名）
technical_fork（技术派生数量）
issue_comments（议题评论数）
4. 贡献者生态（Contributor Ecosystem）
分析项目的社区健康度和风险

bus_factor（巴士因子）
bus_factor_detail（巴士因子详情）
activity_details（活跃度详情）
contributor_email_suffixes（贡献者邮箱后缀分布）
new_contributors（新贡献者数量）
new_contributors_detail（新贡献者详情）
inactive_contributors（不活跃贡献者数量）
participants（参与者总数）
5. Issue 生命周期（Issue Lifecycle）
评估项目的维护质量和响应速度

issues_new（新增议题数）
issues_closed（已关闭议题数）
issues_and_change_request_active（活跃的议题和变更请求数）
issue_age（议题年龄分布）
issue_resolution_duration（议题解决时长）
issue_response_time（议题响应时间）
issue_comments（议题评论数）
6. PR & 代码变更（Pull Request & Code Changes）
展示项目的开发活动强度

change_requests（变更请求数量）
change_requests_accepted（已接受的变更请求数量）
change_requests_reviews（变更请求评审数）
change_request_age（变更请求年龄）
change_request_resolution_duration（变更请求解决时长）
change_request_response_time（变更请求响应时间）
code_change_lines_add（新增代码行数）
code_change_lines_remove（删除代码行数）
code_change_lines_sum（净增代码行数）
7. 社区关注度（Community Attention）
衡量项目的受欢迎程度和社区参与度

attention（关注度）
stars（星标数）
technical_fork（技术派生数量）
participants（参与者总数）
issue_comments（议题评论数）
change_requests_reviews（变更请求评审数）
每个板块都会重点突出相关指标，同时也可以通过交叉引用其他板块的数据来提供更全面的分析视角。这样的分块方式可以帮助用户从不同维度深入了解开源项目的各个方面。