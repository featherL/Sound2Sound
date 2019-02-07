var Client = function(url){
    window.AudioContext = window.AudioContext || window.webkitAudioContext || window.mozAudioContext || window.msAudioContext;

    try {
        var audioContext = new window.AudioContext();
    } catch (e) {
        //Console.log('!Your browser does not support AudioContext');
        throw new Error('您的浏览器不支持AudioContext！');
    }

    try{
        var socket = io.connect(url);
        this.socket = socket;
    } catch(e){
        throw new Error('您的浏览器不支持WebSocket或者网络连接失败！');
    }

    var connected = false;  //是否正在连接
    var first = false;
    var count = 1;  //debug
    var queue = new Array();
    queue.pop = queue.shift;

    socket.on('connect', function(){  //连接成功
        connected = true;
        first = true;
    });

    socket.on('data', function(res){
        //console.log(res.data);
        audioContext.decodeAudioData(res.data, function(buffer){
            queue.push(buffer);
            //console.log(count + ':解码数据长度：' + buffer.length);  //debug
            //count++;  //debug


            if(first){  //第一个数据就播放
                first = false;
                var source = audioContext.createBufferSource();
                source.buffer = buffer;

                source.onended = function callback(){  //播放完后自动播放下一首
                    if(!connected){
                        return;
                    }

                    var next = audioContext.createBufferSource();

                    if(queue.length > 1){
                        queue.pop();
                        //count++;  //debug
                    }

                    next.buffer = queue[0];  //从队列中获取一个解码后的数据

                    next.onended = callback;

                    next.connect(audioContext.destination);
                    next.start(0);

                    //console.log('播放第' + count + '个音频'); //debug
                };

                source.connect(audioContext.destination);
                source.start(0);

                //console.log('播放第' + count + '个音频'); //debug
            }
        });
    });

    socket.on('disconnect', function(){  //失去连接
        connected = false;
        first = false;
    });
}
