<p align="center">
  <img src="daily_todo/resources/robotics-mark.svg" width="72" height="72" alt="Robotics planner logo">
</p>

<h1 align="center">Daily To-do · Việc mỗi ngày</h1>

<p align="center">
  Lịch và danh sách công việc ngay trên desktop Ubuntu.<br>
  Giao diện lấy cảm hứng từ robotics · Tiếng Việt / English · Lưu dữ liệu trên máy
</p>

Một bảng kế hoạch cá nhân để bạn xem hôm nay cần làm gì, ghi việc cho những ngày sắp tới và đánh dấu công việc đã hoàn thành. Tông graphite, cyan và xanh mint tạo cảm giác như một bảng điều khiển trong phòng lab, đồng thời giữ thao tác đơn giản.

## Tính năng

- Lịch tháng: chọn ngày để xem, thêm, xóa và đánh dấu hoàn thành công việc.
- Mỗi ngày có danh sách riêng; ô lịch hiển thị số việc còn lại.
- Thanh tiến độ hoàn thành và xem nhanh công việc khi di chuột lên ngày.
- Chuyển **VI / EN** ngay trong giao diện; nhớ lựa chọn sau khi mở lại.
- Đồng hồ cập nhật mỗi giây theo **giờ Hà Nội (UTC+7)**.
- Khi đang xem hôm nay, danh sách tự chuyển ngày qua nửa đêm hoặc sau khi máy thức dậy.
- **Di chuyển → kéo vùng tên ứng dụng → Ghim tại đây** để lưu vị trí.
- Tự mở sau khi đăng nhập Ubuntu nếu bật autostart.
- Tích hợp GNOME giữ bảng sau các cửa sổ ứng dụng, trên bề mặt desktop để vẫn nhận chuột.
- Ẩn cửa sổ khỏi dock và Alt+Tab.
- Lưu bằng JSON trên máy; không yêu cầu tài khoản, không có đồng bộ đám mây.

## Yêu cầu và phạm vi hỗ trợ

| Thành phần | Yêu cầu |
| --- | --- |
| Môi trường mục tiêu | Ubuntu Desktop 24.04, GNOME Shell 46 |
| Python | Python hệ thống; mã nguồn dùng Python 3.9 trở lên |
| Giao diện | GTK 3, PyGObject |
| Phiên Wayland | Cần XWayland và biến môi trường `DISPLAY` |
| Ghim desktop | Phần mở rộng GNOME đi kèm, hiện khai báo hỗ trợ Shell 46 |
| Kích thước mặc định | 980 × 650; cần vùng màn hình đủ lớn ở mức scale đang dùng |

Ứng dụng đã được kiểm tra trên môi trường Ubuntu/GNOME 46. Các phiên bản GNOME khác, KDE, Xfce, Windows và macOS chưa được xác nhận hỗ trợ. Nếu phần tích hợp GNOME chưa hoạt động, giao diện có thể chạy như cửa sổ thường nhưng **chưa có hành vi ghim desktop đầy đủ**.

Đây là ứng dụng chạy từ mã nguồn; chưa có gói cài đặt `.deb` hoặc AppImage.

## Cài đặt

### 1. Tải mã nguồn

Trên trang GitHub của dự án, chọn **Code → Download ZIP**, giải nén và mở Terminal trong thư mục chứa `app.py`.

Hoặc sao chép **HTTPS clone URL** tại nút Code rồi chạy:

~~~bash
git clone <HTTPS-URL-CUA-REPOSITORY> daily-todo
cd daily-todo
~~~

Thay `<HTTPS-URL-CUA-REPOSITORY>` bằng URL thật của repository, không nhập nguyên phần trong dấu ngoặc.

Nên đặt mã nguồn ở một thư mục cố định, ví dụ `~/Applications/daily-todo`.

### 2. Cài thư viện hệ thống

Trên Ubuntu:

~~~bash
sudo apt update
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 xwayland tzdata
~~~

Kiểm tra GTK:

~~~bash
/usr/bin/python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK', Gtk.MAJOR_VERSION)"
~~~

Dùng **`/usr/bin/python3`** trong các lệnh bên dưới. Python trong Conda hoặc virtualenv có thể không nhìn thấy PyGObject được cài qua apt. Không cần chạy `pip install` hay tạo virtualenv cho cách cài này.

### 3. Chạy thử

Tại thư mục dự án:

~~~bash
/usr/bin/python3 app.py
~~~

Bạn cũng có thể chạy dưới dạng Python package từ thư mục gốc:

~~~bash
/usr/bin/python3 -m daily_todo
~~~

Đến đây, bạn có thể thử thêm công việc, đổi ngôn ngữ và chọn vị trí. Để bảng luôn nằm sau các ứng dụng khác, tiếp tục cài tích hợp desktop ở bước 4.

### 4. Bật ghim desktop và tự khởi động

Kiểm tra phiên bản GNOME:

~~~bash
gnome-shell --version
~~~

Với **GNOME Shell 46**, chạy:

~~~bash
/usr/bin/python3 setup.py --autostart --corner
~~~

Sau đó **lưu công việc đang mở, đăng xuất rồi đăng nhập lại một lần**. GNOME cần phiên đăng nhập mới để nạp extension vừa cài.

Lệnh này:

- Tạo mục **Việc mỗi ngày** trong danh sách ứng dụng.
- Tạo cấu hình tự mở khi đăng nhập cho tài khoản hiện tại.
- Cài và bật extension `daily-todo-desktop@local`.
- Tắt cấu hình phần ghim `daily-todo-corner@local` cũ của dự án nếu có.

**Không chạy `setup.py` bằng sudo.** Script cài cho người dùng hiện tại và lưu đường dẫn tuyệt đối đến mã nguồn. Nếu đổi tên hoặc di chuyển thư mục dự án, chạy lại lệnh cài từ vị trí mới.

Các cách cài khác:

| Lệnh | Tác dụng |
| --- | --- |
| `/usr/bin/python3 setup.py` | Chỉ tạo mục trong danh sách ứng dụng |
| `/usr/bin/python3 setup.py --autostart` | Tạo mục ứng dụng và tự mở khi đăng nhập |
| `/usr/bin/python3 setup.py --corner` | Tạo mục ứng dụng và cài tích hợp GNOME |
| `/usr/bin/python3 setup.py --autostart --corner` | Cài đầy đủ |

## Sử dụng

| Bạn muốn làm gì? | Thao tác |
| --- | --- |
| Ghi việc cho một ngày | Chọn ngày trên lịch, nhập nội dung rồi nhấn **Enter** hoặc **Thêm / Add** |
| Đánh dấu hoàn thành | Bấm ô chọn cạnh công việc |
| Xóa công việc | Bấm biểu tượng thùng rác của dòng đó |
| Xem tháng khác | Dùng nút **‹ / ›** |
| Quay về ngày hiện tại | Bấm **Về hôm nay / Go to today** |
| Đổi ngôn ngữ | Chọn **VI · Tiếng Việt / EN · English** ở đầu bảng |
| Chọn vị trí đặt bảng | Bấm **Di chuyển / Move**, kéo vùng tên ứng dụng rồi bấm **Ghim tại đây / Pin here** |
| Đóng bảng | Bấm **×**; dữ liệu đã thêm vẫn được giữ |
| Mở lại sau khi đóng | Tìm **Việc mỗi ngày** trong danh sách ứng dụng hoặc chạy `/usr/bin/python3 app.py` |

Khi phần tích hợp hoạt động, nhãn trạng thái hiển thị **Ghim desktop / Desktop pinned**. Bảng ở trên mọi workspace, phía sau các cửa sổ ứng dụng. Hãy quay về vùng desktop đang trống để tương tác; ứng dụng khác vẫn che bảng ở phần màn hình mà chúng chiếm.

Autostart có nghĩa là **sau khi đăng nhập tài khoản**, không phải trước màn hình đăng nhập. Nếu bạn chủ động đóng bảng, nó không tự mở lại ngay; hãy mở bằng launcher hoặc chờ lần đăng nhập tiếp theo.

## Tùy chỉnh cho riêng bạn

Đóng rồi mở lại ứng dụng sau khi sửa mã nguồn hoặc CSS.

| Muốn thay đổi | Vị trí chỉnh sửa |
| --- | --- |
| Màu nền, màu nhấn, chữ, viền, khoảng cách | [style.css](daily_todo/resources/style.css) |
| Biểu tượng cánh tay robot trong giao diện | [daily_todo/resources/robotics-mark.svg](daily_todo/resources/robotics-mark.svg) |
| Câu chữ tiếng Việt / tiếng Anh | Từ điển `TEXT` trong [i18n.py](daily_todo/i18n.py) |
| Kích thước cửa sổ | `self.window.set_default_size(980, 650)` trong [app.py](daily_todo/app.py) |
| Bố cục lịch và danh sách | Hàm `build_window()` trong [app.py](daily_todo/app.py) |
| Múi giờ | `HANOI = ZoneInfo(...)` trong [app.py](daily_todo/app.py) |
| Cách giới hạn vị trí theo màn hình | [positioning.py](daily_todo/positioning.py) |
| Cơ chế giữ bảng sau các ứng dụng | [integrations/gnome-shell/extension.js](integrations/gnome-shell/extension.js) |

Ví dụ đổi màu nút thêm và ô ngày đang chọn trong `daily_todo/resources/style.css`:

~~~css
button.primary {
    background-color: #91dfbf;
    border-color: #91dfbf;
    color: #08251b;
}

button.day.selected {
    background-color: #203b34;
    border-color: #91dfbf;
}
~~~

Đây là **GTK CSS**, không phải CSS trình duyệt; chỉ sử dụng thuộc tính GTK hỗ trợ.

Để dùng múi giờ khác, ví dụ:

~~~python
HANOI = ZoneInfo('Asia/Tokyo')
~~~

Đồng thời sửa giá trị `timezone` ở cả hai ngôn ngữ trong `daily_todo/i18n.py` để nhãn đồng hồ hiển thị đúng. Thay đổi này áp dụng cho lịch và đồng hồ; công việc cũ vẫn giữ ngày đã lưu, không tự chuyển đổi sang múi giờ mới.

Nếu sửa extension, chạy lại `setup.py --corner` rồi đăng xuất/đăng nhập để nạp mã mới. Chỉ đổi `shell-version` trong metadata không bảo đảm tương thích với phiên bản GNOME khác.

## Dữ liệu và sao lưu

Các đường dẫn mặc định:

| Nội dung | Tệp |
| --- | --- |
| Công việc theo ngày | `~/.local/share/daily-todo/tasks.json` |
| Vị trí đã ghim | `~/.config/daily-todo/position.json` |
| Ngôn ngữ | `~/.config/daily-todo/settings.json` |
| Tự khởi động | `~/.config/autostart/daily-todo.desktop` |
| Launcher | `~/.local/share/applications/daily-todo.desktop` |
| Extension | `~/.local/share/gnome-shell/extensions/daily-todo-desktop@local/` |

Nếu đặt `XDG_DATA_HOME` hoặc `XDG_CONFIG_HOME`, ứng dụng dùng các thư mục tương ứng thay cho đường dẫn mặc định.

Để sao lưu hoặc chuyển máy: đóng ứng dụng, sao chép các thư mục `daily-todo` chứa dữ liệu và cấu hình sang nơi an toàn. Trên máy mới, cài mã nguồn và thư viện rồi khôi phục các tệp vào vị trí tương ứng.

Công việc được tự lưu khi thêm, xóa hoặc đánh dấu hoàn thành. Nội dung còn đang gõ trong ô nhập chưa được lưu cho đến khi nhấn Enter/Thêm.

## Cập nhật

1. Đóng ứng dụng.
2. Nếu dùng Git, chạy `git pull` trong thư mục dự án; nếu dùng ZIP, cập nhật các tệp mã nguồn.
3. Chạy lại `/usr/bin/python3 setup.py --autostart --corner` nếu bạn dùng cài đặt đầy đủ.
4. Nếu extension thay đổi, đăng xuất/đăng nhập một lần.

Dữ liệu cá nhân được lưu ngoài thư mục mã nguồn. Giữ lại các chỉnh sửa cá nhân trong CSS/mã nguồn trước khi cập nhật để tránh ghi đè chúng.

## Xử lý sự cố

**Lỗi `No module named gi` hoặc không tìm thấy GTK**

Cài thư viện ở bước 2 và dùng `/usr/bin/python3` thay cho Python của Conda/virtualenv.

**Bảng chưa ghim desktop hoặc vẫn hiện như cửa sổ thường**

Kiểm tra GNOME 46, chạy lại `setup.py --autostart --corner`, rồi đăng xuất/đăng nhập. Nếu đã tắt toàn bộ extension người dùng, bật lại trong ứng dụng **Extensions**.

~~~bash
gnome-extensions info daily-todo-desktop@local
~~~

**Không thấy bảng trong dock/Alt+Tab**

Đây là hành vi chủ đích. Quay về desktop hoặc tìm **Việc mỗi ngày** trong danh sách ứng dụng. Trong chế độ desktop, mở launcher không ép bảng đè lên ứng dụng đang làm việc.

**Bảng có vẻ không nhận chuột**

Trước hết bảo đảm không có cửa sổ khác đang che vùng bảng. Không tự bật **Always on Top** hoặc **Always on Bottom**; phần tích hợp GNOME cần giữ bảng trên bề mặt desktop nhưng sau ứng dụng. Nếu lỗi vẫn xảy ra, ghi lại phiên bản GNOME và trạng thái extension khi báo lỗi.

**Bảng quá lớn hoặc bị cắt**

Kích thước mặc định cố định là 980 × 650. Thử giảm mức scale hoặc chỉnh kích thước/bố cục trong `daily_todo/app.py` cho phù hợp màn hình.

**Không tự mở khi bật máy**

Kiểm tra tệp autostart và đường dẫn đến mã nguồn. Nếu đã di chuyển thư mục dự án, chạy lại script cài đặt. Ứng dụng chỉ tự mở khi bạn đăng nhập vào phiên desktop.

## Tắt tự khởi động và gỡ cài đặt

Đóng ứng dụng trước. Để chỉ tắt autostart, xóa tệp `daily-todo.desktop` trong thư mục autostart của tài khoản.

Để gỡ tích hợp GNOME:

~~~bash
gnome-extensions disable daily-todo-desktop@local
~~~

Sau đó xóa launcher, tệp autostart và thư mục extension theo bảng đường dẫn ở trên. Bạn có thể xóa thư mục mã nguồn khi không còn sử dụng.

Dữ liệu công việc và cấu hình cá nhân không tự bị xóa. Giữ chúng để cài lại hoặc sao lưu; chỉ xóa riêng nếu bạn muốn bỏ toàn bộ dữ liệu.

## Cấu trúc dự án và kiểm tra

~~~text
.
├── daily_todo/                   # Mã nguồn ứng dụng
│   ├── __init__.py
│   ├── __main__.py               # python3 -m daily_todo
│   ├── app.py                    # Giao diện và thao tác công việc
│   ├── i18n.py                   # Tiếng Việt / English
│   ├── positioning.py            # Tọa độ và vùng làm việc
│   └── resources/
│       ├── style.css             # Giao diện robotics
│       └── robotics-mark.svg
├── integrations/
│   └── gnome-shell/              # Phần tích hợp desktop GNOME
│       ├── extension.js
│       └── metadata.json
├── scripts/
│   └── install.py                # Cài launcher, autostart và extension
├── tests/                        # Unit test và kiểm tra giao diện
├── app.py                        # Giữ tương thích với launcher cũ
├── setup.py                      # Giữ tương thích với lệnh cài cũ
├── .gitignore
└── README.md
~~~

Kiểm tra logic không cần thao tác desktop:

~~~bash
/usr/bin/python3 -m unittest discover -s tests
~~~

Hai bài thử tích hợp cần chạy riêng khi phát triển:

- `/usr/bin/python3 tests/gui_input_smoke.py`: mở cửa sổ thử, dùng chuột và bàn phím thật, khôi phục vị trí con trỏ sau khi kết thúc.
- `/usr/bin/python3 tests/gnome_stack_smoke.py`: tạo phiên GNOME headless riêng để kiểm tra xếp lớp cửa sổ; cần GNOME Shell, D-Bus và môi trường đồ họa tương thích.

Các bài thử này dùng dữ liệu tạm riêng. Bài thử GUI kiểm tra thao tác nhập liệu; bài thử GNOME kiểm tra thứ tự cửa sổ bằng các cửa sổ mẫu. Chúng không thay thế hoàn toàn việc kiểm tra trên từng cấu hình desktop thực tế.

## Giới hạn hiện tại

- Chưa có nhắc việc, công việc lặp lại, đồng bộ giữa máy hoặc kéo thả công việc giữa các ngày.
- Chưa có sửa trực tiếp nội dung công việc đã tạo; có thể xóa và thêm lại.
- Việc chưa hoàn thành không tự chuyển sang ngày hôm sau.
- Khi đang xem một ngày khác, ứng dụng giữ ngày đó; nhấn **Về hôm nay** để quay lại.
- Múi giờ và kích thước được tùy chỉnh trong mã nguồn, chưa có trang cài đặt riêng.
- Extension hiện nhắm GNOME 46; cần kiểm thử thêm trước khi hỗ trợ phiên bản khác.
- Hành vi của phím **Hiện màn hình nền / Super+D** có thể phụ thuộc GNOME và các extension khác; chưa được xác nhận trên mọi cấu hình.

## Đóng góp

Bạn có thể mở Issue để báo lỗi hoặc đề xuất tính năng. Khi báo lỗi, hãy ghi phiên bản Ubuntu/GNOME, loại phiên X11/Wayland, các bước tái hiện và thông báo trong Terminal nếu có. Không gửi tệp công việc cá nhân khi không cần thiết.

Nếu gửi Pull Request, mô tả thay đổi và cách bạn đã kiểm tra. Các sửa đổi giao diện nên được kiểm tra ở cả tiếng Việt và tiếng Anh.

Dự án hiện chưa có tệp `LICENSE`. Chủ repository có thể bổ sung giấy phép phù hợp trước khi công bố điều kiện sử dụng, sửa đổi và phân phối mã nguồn.

## English quick start

A robotics-inspired desktop planner for Ubuntu GNOME 46, with Vietnamese/English UI, local JSON storage and a Hanoi clock.

1. Download this repository as ZIP or clone its HTTPS URL.
2. Open a terminal in the project directory.
3. Install the system dependencies and run:

~~~bash
sudo apt update
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 xwayland tzdata

/usr/bin/python3 app.py
~~~

For desktop integration and automatic startup after signing in:

~~~bash
/usr/bin/python3 setup.py --autostart --corner
~~~

**Sign out and back in once** to load the GNOME extension. Do not run the setup script with sudo. Keep the source folder in place, or rerun setup after moving it.

Select **EN · English** in the app. Use **Move → drag the title → Pin here** to save its location. In desktop mode, the planner stays behind application windows and is hidden from the dock/Alt+Tab.

Customize `daily_todo/resources/style.css` for colors and fonts, `daily_todo/i18n.py` for UI text, and `daily_todo/app.py` for layout, window size and time zone. Tasks live under `~/.local/share/daily-todo/`; preferences live under `~/.config/daily-todo/`. Other GNOME versions and desktop environments are not yet confirmed supported.
