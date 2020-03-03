if ($ === undefined) $ = CTFd.lib.$;
$.cachedScript = function (url, options) {
    options = $.extend(options || {}, {
        dataType: "script",
        cache: true,
        url: url
    });
    return $.ajax(options);
};
CTFd._internal.challenge.data = undefined;

CTFd._internal.challenge.renderer = CTFd.lib.markdown({});

CTFd._internal.challenge.preRender = function () {
    if (typeof CodeMirror === 'undefined') {
        $.cachedScript(
            CTFd.config.urlRoot + "/plugins/ctfd-acm-challenges/assets/vendor/codemirror.min.js"
        )
    }
};

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown);
};


CTFd._internal.challenge.postRender = function () {
    var lang_map = {
        'python2': 'python',
        'python3': 'python',
        'cpp': 'clike',
        'java': 'clike'
    };
    var mode_map = {
        'python2': 'python',
        'python3': 'python',
        'java': 'text/x-java',
        'cpp': 'text/x-c++src'
    };
    var lang = $('#submission-language').val();
    var mode = mode_map[lang];
    if (mode === undefined) return;
    if (typeof CodeMirror == 'undefined')
        $.cachedScript(CTFd.config.urlRoot + '/plugins/ctfd-acm-challenges/assets/vendor/codemirror.min.js');

    $.cachedScript(
        CTFd.config.urlRoot +
        '/plugins/ctfd-acm-challenges/assets/vendor/' +
        lang_map[lang] + '.min.js'
    ).done(function (script, textStatus) {
        if (typeof CTFd._internal.challenge.data.editor != 'undefined') {
            CTFd._internal.challenge.data.editor.setOption('mode', mode);
            return
        }
        var editor = CodeMirror.fromTextArea(document.getElementById("submission-input"), {
            lineNumbers: true,
            lineWrapping: true,
            styleActiveLine: true,
            autoRefresh: true,
            mode: mode,
            theme: 'mdn-like',
        });

        editor.on('change', function () {
            editor.save();
        });

        setTimeout(function () {
            editor.refresh();
            console.log('codemirror refreshed');
        }, 200);
        CTFd._internal.challenge.data.editor = editor;
    });
};

CTFd._internal.challenge.submit = function (preview) {
    let challenge_id = parseInt($('#challenge-id').val());
    let submission = CTFd._internal.challenge.data.editor.getValue();
    let language = $('#submission-language').val();
    if (language === "") {
        CTFd.ui.ezq.ezAlert({
            title: "Language Undefined!",
            body: "请选择语言",
            button: "Got it!"
        });
        return;
    }
    let params = {
        'challenge_id': challenge_id,
        'submission': btoa(submission),
        'language': language,
    };
    CTFd.api.post_challenge_attempt(
        preview ? {'preview': true} : {}, params).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response;
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response;
        }
        return response;
    });
};