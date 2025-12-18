现在三个后端都已经跑通了：这三个后端分别是：
1、backend\fork_prediction.py
2、backend\indicators_stat.py
3、backend\predict_response_time_xgboost.py

他们都可以进行预测，但是目前还没有进行集成，我现在希望这三个后端都可以集成为一个个方法，方便进行调用。

我的要求如下：
1、对于backend\fork_prediction.py文件执行，其中涉及到选择对应的