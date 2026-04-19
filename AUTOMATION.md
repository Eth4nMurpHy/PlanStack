# PlanStack 自动化说明

这个仓库现在支持一个三阶段流程：

1. 先发布下一天的计划到单独的 next 页面。
2. 当天继续在首页补写 review。
3. 最后再归档当天页面，并把 next 页面切换成新的首页。

## 第一阶段：发布下一天计划

在仓库根目录打开 PowerShell，运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_tomorrow_plan.ps1
```

这个脚本会：

1. 默认用今天的 docs/index.md 生成下一天草稿。
2. 默认用记事本打开这个草稿。
3. 等你保存并关闭文件。
4. 把结果发布到 docs/next.md。

默认生成草稿时会：

1. 把日期改成下一天。
2. 保留你当天页面的大部分结构和内容，方便接着改。
3. 清空 Review 里的 Finished、Feeling、Tomorrow。
4. 把已经勾选的任务重置成未勾选。

如果你这次就是想从零开始写 next，而不是从首页派生，可以运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_tomorrow_plan.ps1 -BlankTemplate
```

如果你不想用记事本，而是想在 VS Code 里编辑草稿，可以运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_tomorrow_plan.ps1 -NoEditor
```

这个模式只会生成草稿并告诉你路径，不会自动打开记事本，也不会自动发布。你改完后可以直接运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_tomorrow_plan.ps1
```

这个脚本会自动找到“明天”对应的草稿并发布到 docs/next.md，不需要你自己再输日期。

这一阶段不会改动 docs/index.md，所以你仍然可以继续在当天首页里写 review。

## 第二阶段：补写当天 review

白天或晚上继续正常编辑 docs/index.md 即可。

Home 页面会一直保持为当天内容，直到你明确执行归档切换。

如果你某天忘了切换，导致首页和 next 页面的日期乱了，可以先运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\sync_plan_dates.ps1
```

这个脚本会自动：

1. 把 docs/index.md 的日期改成今天。
2. 把 docs/next.md 的日期改成明天。
3. 如果 docs/next.md 还是占位页，就直接生成明天模板。

## 第三阶段：归档并切换首页

当你确认当天 review 写完后，运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\complete_day.ps1
```

这个脚本现在会先自动检查和整理状态，然后才归档。它会：

1. 自动把 docs/index.md 的日期对齐到今天。
2. 自动把 docs/next.md 的日期对齐到明天。
3. 检查 next 页面是不是一份真正可切换的明日计划。
4. 如果检查通过，再把 docs/index.md 归档到 docs/History/YYYY-MM-DD.md。
5. 用 docs/next.md 的内容替换 docs/index.md。
6. 把 docs/next.md 重置为空占位页。
7. 自动重建 docs/History/index.md。

如果 next 页面还没准备好，它会直接告诉你先运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\capture_tomorrow_plan.ps1
```

## Windows 每日提醒

如果你想在每天 21:30 自动提醒自己执行第一阶段，可以运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_daily_plan_task.ps1
```

如果你想换成别的时间，例如 20:45：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\register_daily_plan_task.ps1 -Time 20:45
```

## 手动命令

把一个已经写好的计划文件直接发布到 next 页面：

```powershell
python .\scripts\planstack.py publish-next --next-plan .\draft.md
```

自动发布明天草稿到 next 页面：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_tomorrow_plan.ps1
```

归档当前首页，并激活已经发布的 next 页面：

```powershell
python .\scripts\planstack.py rollover
```

只重建历史索引：

```powershell
python .\scripts\planstack.py rebuild-history
```

为某个日期生成一个空白模板：

```powershell
python .\scripts\planstack.py new-template --date 2026-04-18 --output .\draft.md
```

按当前首页内容派生出下一天草稿：

```powershell
python .\scripts\planstack.py derive-template --date 2026-04-18 --output .\draft.md
```

自动把首页日期对齐到今天，并把 next 页面日期对齐到明天：

```powershell
python .\scripts\planstack.py sync-dates
```

## GitHub Pages 部署

[.github/workflows/deploy.yml](.github/workflows/deploy.yml) 会在你 push 到 main 或 master 时自动构建并部署站点。

你还需要在 GitHub 仓库设置里，把 Pages 的来源切换为 GitHub Actions。

如果你不想每次手动输入 git add / commit / push，可以直接运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_site.ps1
```

如果你想自己写提交说明，可以运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_site.ps1 -Message "Update review for 2026-04-18"
```

这个脚本会自动：

1. 检查是否有未提交变更。
2. 执行 git add .。
3. 执行 git commit。
4. 执行 git push。