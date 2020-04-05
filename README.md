# AutoRobotOnlinePlusMofidTrader
در این کد  پایتون می توان به صورت خودکار به مفید آنلاین وصل شد و راس ساعاتی مشخص خرید انجام داد یعنی می توان در صف خرید در ابتدای صبح قرار گرفت

در صورتی که در لینوکس این برنامه را اجرا می کنید با اجرای کد زیر می توانید وارد آنلاین پلاس شود پس از وارد گردن نام کاربری خود و وارد شدن به سایت آلاین مفید این قطعه کد کوکی سایت را ذخیره می کند تا با سرعت بالا توس قطعه کد دوم به خرید راس ساعت ۸:۳۰ دقیقه با دقت میلی ثانیه بپردازید

1- install python3 and chromeWebDriver

2- install dependencies
    # ./installation.sh

3-insert send Order in OrderList.json
    change Time of order with "absoluteTime"
    change repeatation Counter with "repeatCount" 
        zero it means : no repeatation
    change repeatation deltaTime with "repeatTime"
        0.1 mean 0.1 seconds after absoluteTime
    change order count by "orderCount"
    change order Price by "orderPrice"
	change symbol of stock by "isin"
        you can read isin by debug mode of chrome when Online Mofid Trader send a request!!
        i must create a UI for user frindly

4-run autoOnlinePlusWebSiteRefresher.sh
    #./autoOnlinePlusWebSiteRefresher.sh

5-run autoBuySymbol.sh
    ./autoBuySymbol.sh