import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.Writer;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashMap;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class NaverBlogCrawler {
	private DateFormat df = new SimpleDateFormat("yyyy-MM-dd");
	private Date start_date;
	private Date end_date;

	public void setDateRange(String start, String end) throws ParseException {
		this.start_date = this.df.parse(start);
		this.end_date = this.df.parse(end);
	}

	public void collectData(String query) throws Exception {
		int total_count = 0;
		int keyword_count = 0;
		Writer out = new BufferedWriter(
				new OutputStreamWriter(new FileOutputStream("./data/" + query + "3.txt"), "UTF-8"));
		Calendar cal = Calendar.getInstance();
		cal.setTime(this.start_date);
		Calendar cal_end = Calendar.getInstance();
		cal_end.setTime(this.end_date);
		for (Date date = cal.getTime(); cal.compareTo(cal_end) <= 0; date = cal.getTime()) {
			String start = this.df.format(date);
			String end = this.df.format(date);
			System.out.println(start);
			String initUrl = "http://section.blog.naver.com/sub/SearchBlog.nhn?type=post&option.keyword=\"" + query
					+ "\"&term=period&option." + "startDate=" + start + "&option." + "endDate=" + end
					+ "&option.page.currentPage=1" + "&option.orderBy=sim";
			Document page = null;
			try {
				page = Jsoup.connect(initUrl).timeout(10000).userAgent("Mozilla").get();
			} catch (Exception e) {
				System.out.println("date pass...");
				break;
			}
			Thread.sleep(2000);
			Elements group_els = page.select("p[class=several_post] > em");
			int total = 0;
			try {
				total = Integer.valueOf(group_els.get(0).text().split("건")[0]).intValue();
			} catch (Exception e) {
				System.out.println("date pass...");
				break;
			}
			int page_count = 0;
			if (total % 10 != 0) {
				page_count = total / 10 + 1;
			} else {
				page_count = total / 10;
			}
			if (page_count > 400) {
				page_count = 400;
			}
			for (int j = 1; j <= page_count; j++) {
				initUrl =

						"http://section.blog.naver.com/sub/SearchBlog.nhn?type=post&option.keyword=\"" + query
								+ "\"&term=period&option." + "startDate=" + start + "&option." + "endDate=" + end
								+ "&option.page.currentPage=" + j + "&option.orderBy=sim";
				Thread.sleep(2000);
				try {
					page = Jsoup.connect(initUrl).timeout(10000).userAgent("Mozilla").get();
				} catch (Exception e) {
					System.out.println(e);
					continue;
				}
				Thread.sleep(1000);
				group_els = page.select("h5 > a");
				for (Element el : group_els) {
					String blog_url = el.attr("abs:href");

					Document temp1_page = null;
					try {
						temp1_page = Jsoup.connect(blog_url).timeout(10000).userAgent("Mozilla").get();
					} catch (Exception e) {
						System.out.println(e);
						continue;
					}
					Elements elems1 = temp1_page.select("frame[src]");
					String src1 = elems1.attr("abs:src");
					Document temp2_page = null;
					try {
						temp2_page = Jsoup.connect(src1).timeout(10000).userAgent("Mozilla").get();
					} catch (Exception e) {
						System.out.println(e);
						continue;
					}
					Document blog_page = null;
					if (!blog_url.endsWith("from=section")) {
						Elements elems2 = temp2_page.select("frame[src]");
						String src2 = elems2.attr("abs:src");
						try {
							blog_page = Jsoup.connect(src2).timeout(10000).userAgent("Mozilla").get();
						} catch (Exception e) {
							System.out.println(e);
							continue;
						}
					} else {
						blog_page = temp2_page;
					}
					Elements title_els = blog_page.select("h3[class=se_textarea]");
					if (title_els.isEmpty()) {
						title_els = blog_page.select("span[class=pcol1 itemSubjectBoldfont]");
					}
					if (title_els.isEmpty()) {
						System.out.println("Couldn't find title... pass");
					} else {
						String blog_title = title_els.get(0).text().trim();

						Elements date_els = blog_page.select("span[class=se_publishDate pcol2 fil5]");
						if (date_els.isEmpty()) {
							date_els = blog_page.select("p[class=date fil5 pcol2 _postAddDate]");
						}
						String blog_date = date_els.get(0).text().trim();

						Elements text_els = blog_page
								.select("div[class=se_component_wrap sect_dsc __se_component_area]");
						if (text_els.isEmpty()) {
							String[] blog_idList = blog_url.split("&");
							String blog_id = null;
							if (blog_idList.length > 1) {
								blog_id = blog_idList[1].split("=")[1];
							} else {
								String[] tempArray = blog_idList[0].split("/");
								blog_id = tempArray[(tempArray.length - 1)].replace("?", "");
							}
							text_els = blog_page
									.select("div[class=post-view pcol2 _param(1) _postViewArea" + blog_id + "]");
						}
						String blog_text = text_els.get(0).text().trim();

						out.write(blog_date + "\t" + blog_title + "\t" + blog_text + "\n");
						total_count++;
						keyword_count++;
						System.out.println(query + "\t" + keyword_count);
					}
				}
			}
			label997: cal.add(5, 1);
		}
		out.close();
		System.out.println("Total :\t" + total_count);
		System.out.println("Completed!");
	}

	protected static HashMap<String, ArrayList<String>> parseArgs(String[] args) {
		HashMap<String, ArrayList<String>> ret = new HashMap();
		String key = null;
		String[] arrayOfString = args;
		int j = args.length;
		for (int i = 0; i < j; i++) {
			String arg = arrayOfString[i];
			if (arg.startsWith("-")) {
				key = arg;
				ret.putIfAbsent(key, new ArrayList());
			} else if (key == null) {
				ret.putIfAbsent(key, new ArrayList());
				((ArrayList) ret.get(key)).add(arg);
			} else {
				((ArrayList) ret.get(key)).add(arg);
				key = null;
			}
		}
		if (key != null) {
			ret.put(key, new ArrayList());
		}
		return ret;
	}

	public static void main(String[] args) {
		System.out.println("Hi~");
		try {
			HashMap<String, ArrayList<String>> am = parseArgs(args);
			ArrayList<String> queryList = null;
			String startDate = "2015-05-12";
			String endDate = "2017-06-01";
			for (String k : am.keySet()) {
				if (k == null) {
					queryList = (ArrayList) am.get(k);
				} else if (k.equals("-date")) {
					try {
						startDate = (String) ((ArrayList) am.get(k)).get(0);
						endDate = (String) ((ArrayList) am.get(k)).get(1);
					} catch (IndexOutOfBoundsException localIndexOutOfBoundsException) {
					}
				}
			}
			if (queryList == null) {
				System.out.println("No query! Please input query.");
				return;
			}
			System.out.println("Start Date: " + startDate);
			System.out.println("End Date: " + endDate);

			NaverBlogCrawler napim = new NaverBlogCrawler();
			napim.setDateRange(startDate, endDate);
			for (String q : queryList) {
				System.out.println("Queries: " + q);
				napim.collectData(q);
			}
		} catch (Exception e) {
			System.out.println(e);
			e.getStackTrace();
		}
		System.out.println("Bye~");
	}
}
