现在三个后端都已经跑通了：这三个后端分别是：
1、backend\fork_prediction.py
2、backend\indicators_stat.py
3、backend\predict_response_time_xgboost.py

他们都可以进行预测，但是目前还没有进行集成，我现在希望这三个后端都可以集成为一个个方法，方便进行调用。

我的要求如下：
1、对于backend\fork_prediction.py文件执行，其中涉及到选择并处理目标列，这里不需要处理了，直接默认选择序列号32即可（直接在源码上进行修改）
2、对于backend\indicators_stat.py,它生成了好几张图片：热力图、标分布直方图、Top10项目对比图，你看看指标统计信息JSON：C:\Users\22390\Desktop\OpenSODA\backendData\indicators_stat.json这个文件里面有没有生成这些图像的信息，如果有，那么就可以发给前端，前端根据这个数据进行相应的可视化，生成对应的统计图即可。
3、对于backend\predict_response_time_xgboost.py，这里也是一样的，根据生成的预测数据进行展示，我看到生成的数据图比较复杂，你先尝试通过返回的json数据（C:\Users\22390\Desktop\OpenSODA\backendData\response_time_prediction_result.json）去在前端生成对应的图像。


所以后端代码都需要做的事：
1、将他们的功能封装成函数，方便backend\main.py进行调用，在main.py中创建相应的请求接口，对应的接口调用就执行相应的算法函数，函数就返回对应生成的json数据，你可以不用走保存为文件这一步了，直接返回json数据。
2、对于backend\predict_response_time_xgboost.py，由于它运行的时间比较久，我前端需要做一个轮询操作，所以说你这边不仅要设计一个启动后台的接口，还要设计一个轮询的接口，对应的进度信息展示你可以参照这些这个文件里面的打印信息：【1/7】加载数据...等等，到时候前端也会进行相应的进度信息展示工作。