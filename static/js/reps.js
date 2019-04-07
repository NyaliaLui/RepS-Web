function _(el) {
    return document.getElementById(el);
  }
  function add_err(msg) {
    let err = document.createElement('li');
    err.innerText = msg;
    let errwindow = _("err__wndow");
    errwindow.appendChild(err);
  }

  function clear_errs() {
    let errwindow = _("err__wndow");
    while (errwindow.firstChild) {
      errwindow.removeChild(errwindow.firstChild);
    }
  }

  function show_btns() {
      let em = document.getElementsByClassName("sort__btn");
      em[0].style.display = "inline-block";
      em[1].style.display = "inline-block";
      _("rename__check").style.display = "inline-block";
  }

  function is_archive(file) {
    
    let filetype = file.type;
    if (file.type == "") {
      filetype = file.name.split(".").pop();
    }

    console.log(filetype);

    return (filetype == "application/zip") ||
     (filetype == "application/x-zip-compressed") ||
     (filetype == "application/zip-compressed") ||
     (filetype == "application/x-rar-compressed") ||
     (filetype == "rar") || (filetype == "zip");
  }

  function validate_file() {
        let file = _("replays").files[0];

        if (file.size > 100000000) {
          add_err("archive size must be less than 100MB");
          return;
        } else if (!is_archive(file)) {
          add_err("file must be a .zip or .rar archive");
          return;
        }
        
        //go ahead and upload the file if the checkbox
        //is checked
        if (_("perm").checked == true) {
          upload_file();
        } else {
          _("replays").style.display = "none";
          _("replays__labl").style.display = "none"
          _("perm__reminder").style.display = "inline-block";
        }
    };

    function validate_checkbox() {
      if (_("perm").checked != true) {
        add_err("permission to store archive is required");
        _("replays").value = null;
      }

      //upload file if replays is set
      if (_("replays").files.length == 1) {
        upload_file();
      } else if (_("replays").files.length > 1) {
        add_err("only upload 1 archive");
      }
    }

    function upload_file() {
      clear_errs();

      //hide replays input
      _("replay__zone").style.display = "none";
      _("replays").style.display = "none";
      _("replays__labl").style.display = "none"
      _("store__perm").style.display = "none";

      //show progress bar
      _("progress__bar").style.display = "inline-block";
      _("status").style.display = "inline-block";
      _("loaded_n_total").style.display = "inline-block";

      let file = _("replays").files[0];
      _("archivename").value = file.name;
      
      let formdata = new FormData();
      formdata.append("perm", _("perm").value);
      formdata.append("replays", file);

      let ajax = new XMLHttpRequest();
      ajax.upload.addEventListener("progress", progress_handler, false);
      ajax.addEventListener("load", complete_handler, false);
      ajax.addEventListener("error", err_handler, false);
      ajax.addEventListener("abort", abort_handler, false);
      ajax.open("POST", '/upload');
      ajax.send(formdata);
    }

    function progress_handler(event) {
      _("loaded_n_total").innerHTML = "Uploaded: " + event.loaded + " / " + event.total;
      let percent = (event.loaded / event.total) * 100;
      _("progress__bar").value = Math.round(percent);
      _("status").innerHTML = Math.round(percent) + "% uploaded";
    }

    function complete_handler(event) {
      let res = JSON.parse(event.target.responseText);
      
      if (res.msg != "success") {
        add_err(res.msg);
      } else {
        //hide progress bar
        _("progress__bar").style.display = "none";
        _("status").style.display = "none";
        _("loaded_n_total").style.display = "none";

        //show sortop btns
        show_btns();

        //clear file out
        _("replay__zone").removeChild(_("replays"));
      }
    }

    function err_handler(event) {
      add_err("Upload Failed");
    }

    function abort_handler(event) {
      add_err("Upload Aborted");
    }