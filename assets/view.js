window.challenge.data = undefined;

window.challenge.renderer = new markdownit({
    html: true,
    linkify: true,
});
var vendor_path = '/plugins/CTFd_ICPC_Challenges/assets/vendor'
jQuery.cachedScript = function (url, options) {
    options = $.extend(options || {}, {
        dataType: "script",
        cache: true,
        url: url
    });
    return jQuery.ajax(options);
};

window.challenge.preRender = function () {
    if (typeof CodeMirror === 'undefined') {
        $.cachedScript(
            script_root + vendor_path + "/codemirror.min.js"
        )
    }
};

window.challenge.render = function (markdown) {
    return window.challenge.renderer.render(markdown);
};


window.challenge.postRender = function () {
    var lang_map = {
        'python2': 'python',
        'python3': 'python',
        'cpp': 'clike',
        'java': 'clike'
    }
    var mode_map = {
        'python2': 'python',
        'python3': 'python',
        'java': 'text/x-java',
        'cpp': 'text/x-c++src'
    }
    var mode = mode_map[$('#submission-language').val()];
    if (mode === undefined) return;
    if (typeof CodeMirror == 'undefined')
        $.cachedScript(script_root + vendor_path + '/codemirror.min.js')

    $.cachedScript(
        script_root +
        vendor_path + "/" +
        lang_map[$('#submission-language').val()] + '.min.js'
    ).done(function (script, textStatus) {
        if (typeof window.challenge.data.editor != 'undefined') {
            window.challenge.data.editor.setOption('mode', mode)
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
        window.challenge.data.editor = editor;
    });
};

function randomString(len) {
    len = len || 32;
    let $chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';
    let maxPos = $chars.length;
    let pwd = '';
    for (let i = 0; i < len; i++) {
        pwd += $chars.charAt(Math.floor(Math.random() * maxPos));
    }
    return pwd;
}

window.challenge.submit = function (cb, preview) {
    let challenge_id = parseInt($('#challenge-id').val());
    let submission = window.challenge.data.editor.getValue();
    let language = $('#submission-language').val();
    if (language === "") {
        ezal({
            title: "Language Undefined!",
            body: "请选择语言",
            button: "Got it!"
        });
        return;
    }
    let url = "/api/v1/challenges/attempt";

    if (preview) {
        url += "?preview=true";
    }
    let params = {
        'submission_nonce': randomString(32),
        'challenge_id': challenge_id,
        'submission': btoa(submission),
        'language': language
    };
    CTFd.fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json'
        },
        body: JSON.stringify(params)
    }).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response.json();
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response.json();
        }
        return response.json();
    }).then(function (response) {
        cb(response);
    });
};