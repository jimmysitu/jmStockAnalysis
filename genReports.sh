#!/bin/bash

OUT_PATH=docs/_includes/reports

# GATAFA
./jmStockAnalysis.py --db sp500.db3 -t GOOGL    -o $OUT_PATH/googl.html
./jmStockAnalysis.py --db sp500.db3 -t AAPL     -o $OUT_PATH/aapl.html
./jmStockAnalysis.py --db hsi.db3   -t 00700    -o $OUT_PATH/00700.html
./jmStockAnalysis.py --db sp500.db3 -t AMZN     -o $OUT_PATH/amzn.html
./jmStockAnalysis.py --db sp500.db3 -t META     -o $OUT_PATH/meta.html
./jmStockAnalysis.py --db sp500.db3 -t AAPL     -o $OUT_PATH/aapl.html
./jmStockAnalysis.py --db hsi.db3   -t 09988    -o $OUT_PATH/09988.html

# AN ATM
./jmStockAnalysis.py --db xnas.db3  -t ASML     -o $OUT_PATH/asml.html
./jmStockAnalysis.py --db sp500.db3 -t NVDA     -o $OUT_PATH/nvda.html

./jmStockAnalysis.py --db sp500.db3 -t AAPL     -o $OUT_PATH/aapl.html
./jmStockAnalysis.py --db sp500.db3 -t TSLA     -o $OUT_PATH/tsla.html
./jmStockAnalysis.py --db sp500.db3 -t MSFT     -o $OUT_PATH/msft.html

# CPU in XNAS
./jmStockAnalysis.py --db sp500.db3 -t INTC     -o $OUT_PATH/intc.html
./jmStockAnalysis.py --db sp500.db3 -t AMD      -o $OUT_PATH/amd.html

# CPU in XSHG
./jmStockAnalysis.py --db xshg.db3 -t 688041    -o $OUT_PATH/688041.html
./jmStockAnalysis.py --db xshg.db3 -t 688047    -o $OUT_PATH/688047.html

# JM's Magic Water
# Starbucks, coffee shop
./jmStockAnalysis.py --db sp500.db3 -t SBUX     -o $OUT_PATH/sbux.html
# Monster Beverage
./jmStockAnalysis.py --db sp500.db3 -t MNST     -o $OUT_PATH/mnst.html
# Coca-Cola, drinks
./jmStockAnalysis.py --db sp500.db3 -t KO       -o $OUT_PATH/ko.html

# JM's Daily Life
# Xiaomi
./jmStockAnalysis.py --db hsi.db3 -t 01810    -o $OUT_PATH/01810.html
# Meituan
./jmStockAnalysis.py --db hsi.db3 -t 03690    -o $OUT_PATH/03690.html
# JingDong
./jmStockAnalysis.py --db hsi.db3 -t 09618    -o $OUT_PATH/09618.html

# Watching List
./jmStockAnalysis.py --db sp500.db3 -t NFLX     -o $OUT_PATH/nflx.html
