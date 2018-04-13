#!/usr/bin/env perl
use Mojo::Webqq;
use Digest::MD5;

#使用 mojo-webqq 作为 webqq 框架（https://github.com/sjdy521/Mojo-Webqq.git）
# nohup perl mojo_webqq_login.pl >> ./qq.log & 2>&1
my ($host,$port,$post_api);

$host = "0.0.0.0"; #发送消息接口监听地址，没有特殊需要请不要修改
$port = 5598;      #发送消息接口监听端口，修改为自己希望监听的端口
$post_api = 'http://127.0.0.1:5599/qqapi/anypost/';  #接收到的消息上报接口，如果不需要接收消息上报，可以删除或注释此行

my $client = Mojo::Webqq->new(
    http_debug  =>  0,         #是否打印详细的debug信息
    log_level   => "info",     #日志打印级别
    log_path    => "/root/qq_monitor_system/qq.log",
    log_encoding => "utf-8",
    update_interval => 300,
    login_type=>"login",
    account=>'2372961723',
    pwd=>Digest::MD5::md5_hex('www.upyun.com,'),
);

$client->load("ShowMsg");

#二维码上传公有云图床生成链接
$client->load("UploadQRcode");

#提供 http 接口
$client->load("Openqq",data=>{listen=>[{host=>$host,port=>$port}], post_api=>$post_api});

=pod
#智能聊天
$client->load("SmartReply",data=>{
    apikey          => '21f2717e82a646e3bebc6a9f4e4a1710', #可选，参考http://www.tuling123.com/html/doc/apikey.html
    #apikey          => '4c53b48522ac4efdfe5dfb4f6149ae51', #可选，参考http://www.tuling123.com/html/doc/apikey.html
    friend_reply    => 1, #是否针对好友消息智能回复
    group_reply     => 1, #是否针对群消息智能回复
    notice_reply    => ["对不起，请不要这么频繁的艾特我","对不起，您的艾特次数太多"], #可选，提醒时用语
    notice_limit    => 8 ,  #可选，达到该次数提醒对话次数太多，提醒语来自默认或 notice_reply
    warn_limit      => 10,  #可选,达到该次数，会被警告
    ban_limit       => 12,  #可选,达到该次数会被列入黑名单不再进行回复
    ban_time        => 1200,#可选，拉入黑名单时间，默认1200秒
    period          => 600, #可选，限制周期，单位 秒
    is_need_at      => 1,  #默认是1 是否需要艾特才触发回复 仅针对群消息
    keyword         => [qw(嗯 恩 是 的)], #触发智能回复的关键字
});
=cut

$client->run();
