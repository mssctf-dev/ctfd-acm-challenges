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

function copyToClipboard(str) {
    const el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}

const codes = []
function update(dir) {
    var table = CTFd.lib.$("#tab_data");
    var page = parseInt(CTFd.lib.$("#page")[0].textContent);
    if (dir !== undefined && page + dir > 0) page += dir;
    else return;
    CTFd.lib.$("#page")[0].textContent = page;
    CTFd.lib.$.ajax({
        url: '/api/v1/acm_chall/submissions/?page=' + page,
        success: function (data) {
            table.empty();
            codes.splice(0, codes.length);
            for (let i = 0; i < data.length; i++) {
                var tr = [
                    `<td>${data[i].user.name}</td>`,
                    `<td>${data[i].challenge.name}</td>`,
                    `<td>${data[i].lang}</td>`,
                    `<td>${data[i].status == 'finished' ?
                        `<span class="status" id="${data[i].result}">
                            ${data[i].result}
                        </span>`:
                        data[i].status}
                    </td>`,
                    `<td>${Moment(data[i].date)
                        .local()
                        .fromNow()}</td>`,
                    `<td>${formatMs(data[i].time)} sec</td>`,
                    `<td>${formatBytes(data[i].memory)}</td>`,
                ];
                if (data[i].code !== undefined) {
                    var head = CTFd.lib.$("#tab_head");
                    if (head[0].lastElementChild.textContent !== "Code")
                        head.append('<th>Code</th>')
                    codes.push(data[i].code);
                    tr.push(
                        `<td><a href="#" 
                        onclick="copyToClipboard(codes[${codes.length - 1}])"
                    >Copy</a></td>`
                    )
                }
                table.append(["<tr>", ...tr, "</tr>"].join(""));
            }
        }
    })
}

update(0);
setInterval(() => update(0), 10000);