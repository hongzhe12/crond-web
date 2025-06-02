
# 定时任务管理系统

## 一、项目概述
本系统基于Flask框架开发，提供可视化的定时任务管理界面，支持通过Cron表达式配置任务执行周期，支持Python和Shell脚本类型，具备任务添加、编辑、删除及日志查看功能。适用于需要自动化执行脚本的场景，如数据同步、监控任务等。


## 二、功能特性
| 功能模块       | 详细说明                                                                 |
|----------------|--------------------------------------------------------------------------|
| **任务管理**   | - 支持通过预设时间（分钟/小时/天/周/月/年）或自定义Cron表达式创建任务<br>- 任务列表展示当前所有Crontab任务，支持编辑和删除操作 |
| **脚本支持**   | - 自动生成脚本文件并存储于`scripts/`目录<br>- 支持Python和Shell脚本类型，自动处理文件权限（Shell脚本添加执行权限） |
| **可视化配置** | - 时间表达式预设下拉菜单（含中文描述）<br>- 实时解析Cron表达式为中文描述，辅助用户配置 |
| **日志系统**   | - （待扩展）计划支持任务执行日志记录与查看（当前代码包含日志页面模板，但未实现日志生成逻辑） |


## 三、目录结构
```
项目根目录
├─ app.py                # 主程序入口
├─ templates/            # 前端模板文件
│  ├─ add.html           # 添加任务页面
│  ├─ edit.html          # 编辑任务页面
│  ├─ index.html         # 任务列表页面
│  ├─ logs.html          # 日志列表页面（待完善）
│  └─ view_log.html      # 日志详情页面（待完善）
└─ scripts/              # 自动生成的脚本存储目录（运行时自动创建）
```


## 四、技术栈
1. **后端**  
   - Flask：Web框架，处理路由和业务逻辑  
   - CronDescriptor：解析Cron表达式为中文描述  
   - Subprocess：调用系统命令操作Crontab和脚本执行  

2. **前端**  
   - Bootstrap 5：响应式布局和UI组件  
   - JavaScript：实现Cron表达式实时解析与表单交互  


## 五、使用说明

### 1. 环境搭建
```bash
# 安装依赖
pip install flask cron_descriptor

# 启动服务（开发环境）
python app.py
```
- 访问 `http://localhost:5000` 进入任务管理界面


### 2. 添加任务
1. 在**添加任务页面**选择时间预设（如“每天凌晨执行一次”）或手动输入Cron表达式  
2. 选择脚本类型（Python/Shell），输入脚本内容  
3. 点击“添加任务”，系统自动生成脚本文件并更新Crontab  

**示例：**  
- Cron表达式：`0 0 * * *`（每天凌晨执行）  
- 脚本内容（Shell）：  
  ```bash
  #!/bin/bash
  echo "Daily cleanup task" >> /var/log/cleanup.log
  ```


### 3. 管理任务
- **编辑任务**：点击任务列表中的“编辑”按钮，修改时间表达式或脚本内容后保存  
- **删除任务**：点击“删除”按钮，系统将同时删除关联的脚本文件（当前未实现日志文件删除，需手动清理）  



## 七、截图预留位置
### 1. 任务列表界面
![QQ_1748661163570](https://github.com/user-attachments/assets/fd51f7ed-0ab4-4cc8-9854-5945439a40bc)

![QQ_1748661204488](https://github.com/user-attachments/assets/6042956b-57e3-4e66-96fc-dbdbfc93019a)

### 2. 添加任务界面
![QQ_1748661188840](https://github.com/user-attachments/assets/8772678a-869b-4718-b4b3-e75a23657974)



## 八、贡献方式
如需参与开发，可通过以下步骤：  
1. 克隆仓库：`git clone https://github.com/hongzhe12/cron-manager.git`  
2. 创建开发分支：`git checkout -b feature/log-system`  
3. 提交代码并发起Pull Request  

