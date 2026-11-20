;;;; start_server.lisp — chạy Andes help server (chế độ KHÔNG cần MySQL)
;;;; Dùng:  sbcl --noinform --disable-debugger --script start_server.lisp
;;;; Yêu cầu: đã cài Quicklisp và giải nén repo vào ~/andes-stable

(load (merge-pathnames "quicklisp/setup.lisp" (user-homedir-pathname)))

(push (merge-pathnames "andes-stable/" (user-homedir-pathname))
      asdf:*central-registry*)

(ql:quickload :andes)
(ql:quickload :andes-help)

;; Bỏ qua MySQL (mất log học sinh). Bỏ dòng này nếu đã cấu hình DB đúng.
(setf andes-database::*skip-db* t)

(start-help :password "x")
(format t "~%SERVER-STARTED-8080~%") (finish-output)
(loop (sleep 3600))
