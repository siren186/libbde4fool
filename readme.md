libbde-msvc傻瓜编译包
----
> 官方仓库: https://github.com/libyal/libbde

官方的仓库 Clone 下来之后,需要配置很多额外的信息,才能开始编译. 这个仓库将官方所依赖的资源做了整合,使之可以更简单的 Clone 下来即可编译


# 所使用到的库版本信息:
|库|版本|链接|
|--|--|--|
|libbde|libbde-alpha-20221031|[libbde-alpha-20221031](https://github.com/libyal/libbde/archive/refs/tags/20221031.zip)|
|dokan|1.5.0.3000|[Dokan-1.5.0.3000](https://github.com/dokan-dev/dokany/releases/download/v1.5.0.3000/DokanSetup.exe)|


# 编译前准备工作
1. 下载并安装[Dokan1经典版(1.5.0.3000)](https://github.com/dokan-dev/dokany/releases/download/v1.5.0.3000/DokanSetup.exe)
2. 编译器要求vs2008及以上版本(我这个仓库用了vs2008的vs2022)