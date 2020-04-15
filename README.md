Quick & dirty solution to pair NBP exchange rates with Bitstamp market operations. For tax documents purposes (namely PIT-38 in Poland).

[Article about cryptocurrencies tax regulations (in polish)](https://www.e-pity.pl/podatek-pit-od-kryptowalut/)

# Usage

[Download archival exchange rates](https://www.nbp.pl/home.aspx?f=/kursy/arch_a.html) get the CSV format
Download bitstamp history (get only market operations - withdrawals etc. are irrelevant)

Parse NBP csv using `parse_nbp.py` (tax.db should be created). It's safe to run this script many times, as there is UNIQUE constraint on the table.

Parse Bitstamp data using `parse_bitstamp.py`. tax.db should be updated. DO NOT run this more than once, as you'll have duplicate entries.

At this point you should probably verify contents of tax.db using any sqlite client.

Run `summarize_year.py`.
