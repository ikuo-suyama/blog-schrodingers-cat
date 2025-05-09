var script = document.createElement('script');
script.charset = 'utf-8';
script.async = true;
script.defer = true;
script.src = '//log000.goo.ne.jp/b.js?id=goo&url=' + escape(document.location) + '&ref=' + escape(document.referrer);
(document.head || document.getElementsByTagName('head')[0]).appendChild(script);
