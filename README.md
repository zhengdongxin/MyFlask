### ORM

    简介：
    对象关系映射（Object Relational Mapping，简称ORM），是一种被广泛使用的开发技术，
    用于实现面向对象编程语言里不同类型系统的数据之间的转换注：此句来自官方。
    通俗的讲，ORM其实是创建了一种可以在程序开发中高效，便捷使用的数据库操作方法，只不过ORM封装了数据库底层的语句。



python 主流的web框架中，一般存在两个重要概念

### application

    概念不讲，默认大家都理解。在项目启动时，会初始化application对象。该对象可以存储项目的全局变量
    如config信息之类的，一般在init app 过程中我们会是初始化其他资源并存储在app中，其实主要就是各种连接池
    mysql、redis、ES、mongoDB等等。

    但是因为app是全局的，而在多线程web框架（flask,django）中每一个请求都在独立的线程中，如何确保不同线程
    合理的获取全局的资源,这里指的是如何确保同一个线程中不会重复获取支援？

    以我熟悉的项目为例
    使用  threading.local()
    https://gitlab.weike.fm/weike/wk_personal_center/blob/bee1a93d4c4e11be2c33d4b6156b59a36d882e57/exts/flask_mysql.py#L8


但其实没有必要，因为有request
### request

    简单解释，其实就是把用对象的形式表示一个http请求，以flask为例，一般提供 app.before_request方法
    帮助开发者往request挂载一些独立线程的资源。比如前面讲的从mysql连接池子获取的连接，具体看代码。




### 使用ORM优点：

    如现有项目中以下代码可以删掉：
    https://gitlab.weike.fm/weike/wk_personal_center/blob/52b325456d593849a9c429e2fd9935ea6efdb54d/lib/operations.py#L47


### 等待优化：

    find 接口可以根据config 优先搜索组合索引、索引等字段

### 不足

    无法支持跨表