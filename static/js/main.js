$(document).ready(function(){
    var opened = false;
    var client;
    $('#switch').on('click', function(){
        if(!opened){
            if(!client){
                try{
                    url = location.protocol + '//' + document.domain + ':' + location.port + '/sound';
                    client = new Client(url);
                } catch(e){
                    alert(e.message);
                    return;
                }
            }else{
                client.socket.connect();
            }

            opened = true;
            $('#switch').text("断开");
        }else{
            if(client){
                client.socket.disconnect();
            }
            opened = false;
            $('#switch').text("连接");
        }

    });
});

