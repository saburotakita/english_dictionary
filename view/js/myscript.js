$(function(){
    // メッセージを変更する
    eel.expose(change_message)
    function change_message(type, text) {
        const $message = $("#message");

        // 現在のクラスを削除
        $message.removeClass("alert-primary");
        $message.removeClass("alert-success");
        $message.removeClass("alert-danger");
        $message.removeClass("alert-secondary");

        // 指定されたクラスをセット
        if (type === "running") {
            $message.addClass("alert-primary");
        } else if (type === "success") {
            $message.addClass("alert-success");
        } else if (type === "error") {
            $message.addClass("alert-danger");
        } else {
            $message.addClass("alert-secondary");
        }

        // メッセージの内容を変更
        $message.html(text)
    }

    // 検索ボタンの有効化、無効化変更
    function change_search_button(state) {
        if (state === "disable") {
            $("#btn-search").prop("disabled", true);
        } else {
            $("#btn-search").prop("disabled", false);
        }
    }

    eel.expose(enable_search_button)
    function enable_search_button() {
        change_search_button("enable")
    }

    eel.expose(disable_search_button)
    function disable_search_button() {
        change_search_button("disable")
    }


    // 検索ボタンのクリック処理
    $("#btn-search").click(() => {
        const site = $('input:radio[name="radios"]:checked').val();
        const import_name = $('#input-import-file').val();
        const export_name = $('#input-export-file').val();
        eel.run(site, import_name, export_name)
    });
});
