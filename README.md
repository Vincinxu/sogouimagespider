# 搜狗图片爬虫

## 爬取过程：
因为搜狗图片加载的方式是Ajax加载，所以此次爬虫采取模拟发送Ajax请求与服务器进行交互获取数据。通过浏览器开发者工具可以筛选到交互返回的XHR格式的文件，然后不
断下拉页面会自动生成新的XHR的文件。通过比较这些XHR文件的请求URL可以发现其中的规律，而且这些URL才是真正爬取的对象，然后根据URL里的请求参数重新构造一个
可动态爬取的URL，与分页爬取的URL一样的格式，然后获取json数据，接着提取json数据，分别保存到mongodb和下载图片到本地。下载图片的方法采用了去重的方式，所
以被下载过的图片只要本地还存在就不会被重新下载并出现重复的图片。图片的文件名则是采用MD5加密后的字符串命名以区分图片。最后还采用多进程进行提高爬取和下载
的效率。

## 采用的技术：
requests，伪装请求头，mongodb，urllib，hashlib.md5，多进程
