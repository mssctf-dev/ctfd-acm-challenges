function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatMs(s) {
    var ms = s % 1000;
    s = (s - ms) / 1000;
    var secs = s % 60;
    return secs + '.' + ms;
}

function update() {
    var table = CTFd.lib.$("#data");
    var page = parseInt(CTFd.lib.$("#page")[0].value);
    CTFd.lib.$("#page")[0].value = page;
    CTFd.lib.$.ajax({
        url: '/api/v1/acm_chall/submissions/?page=' + page,
        success: function (data) {
            table.empty();
            for (let i = 0; i < data.length; i++) {
                var tr = [
                    "<tr>",
                    `<td>${data[i].user.name}</td>`,
                    `<td>${data[i].challenge.name}</td>`,
                    `<td>${data[i].status}</td>`,
                    `<td>${data[i].lang}</td>`,
                    `<td><span class="status" id="${data[i].result}">
                        ${data[i].result}
                    </span></td>`,
                    `<td>${Moment(data[i].date)
                        .local()
                        .fromNow()}</td>`,
                    `<td>${formatMs(data[i].time)} sec</td>`,
                    `<td>${formatBytes(data[i].memory)}</td>`,
                    "</tr>"
                ].join("");
                table.append(tr);
            }
        }
    })
}

(function () {
    window.inputNumber = function (el) {

        var min = el.attr('min') || false;
        var max = el.attr('max') || false;

        var els = {};

        els.dec = el.prev();
        els.inc = el.next();

        el.each(function () {
            init(CTFd.lib.$(this));
        });

        function init(el) {

            els.dec.on('click', decrement);
            els.inc.on('click', increment);

            function decrement() {
                var value = el[0].value;
                value--;
                if (!min || value >= min) {
                    el[0].value = value;
                    update();
                }
            }

            function increment() {
                var value = el[0].value;
                value++;
                if (!max || value <= max) {
                    el[0].value = value++;
                    update();
                }
            }
        }
    }
})();

inputNumber(CTFd.lib.$('#page'));


(function () {
    var spinnerint;
    var waittime = 10000;
    var loadtime = 1000;

    function showSpinner() {
        CTFd.lib.$("#spinner svg").attr("class", "waiting");
        spinnerint = setTimeout(showLoader, waittime);
    }

    function showLoader() {
        CTFd.lib.$("#spinner svg").attr("class", "loading");
        update();
        spinnerint = setTimeout(showSpinner, loadtime);
    }

    var spinner = CTFd.lib.$("#spinner");
    spinner.click(function () {
        clearTimeout(spinnerint);
        if (spinner.attr("class") === "active") {
            spinner.attr("class", "inactive");
        } else {
            spinner.attr("class", "active");
            showLoader();
        }
    });
    spinner.attr("class", "active");
    showLoader();
    CTFd.lib.$("#page").change(showLoader);
})();
