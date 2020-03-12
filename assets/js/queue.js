function update() {
    var table = CTFd.lib.$("#data");
    var page = parseInt(CTFd.lib.$("#page")[0].value);
    CTFd.lib.$("#page")[0].value = page;
    table.empty();
    table.append(
        '<tr>\n' +
        '    <th>ID</th>\n' +
        '    <th>Author</th>\n' +
        '    <th>Status</th>\n' +
        '    <th>Language</th>\n' +
        '    <th>Result</th>\n' +
        '    <th>Date</th>\n' +
        '    <th>Time</th>\n' +
        '    <th>Memory</th>\n' +
        '</tr>');
    CTFd.lib.$.ajax({
        url: '/api/v1/acm_chall/submissions/?page=' + page,
        success: function (data) {
            for (let i = 0; i < data.length; i++) {
                var tr = [
                    "<tr>",
                    "<th>" + (i + 1) + "</th>",
                    "<th>" + data[i].author + "</th>",
                    "<th>" + data[i].status + "</th>",
                    "<th>" + data[i].lang + "</th>",
                    "<th>" + data[i].result + "</th>",
                    "<th>" + data[i].date + "</th>",
                    "<th>" + data[i].time + "</th>",
                    "<th>" + data[i].memory + "</th>",
                    "</tr>"
                ].join("");
                table.append(tr);
            }
        }
    })
}

CTFd.lib.$("#page").change(update);
update();
setInterval(update, 10000);
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