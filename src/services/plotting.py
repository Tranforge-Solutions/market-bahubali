import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for thread safety
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)

class ChartService:
    def generate_chart(self, df: pd.DataFrame, ticker: str) -> io.BytesIO:
        """
        Generates a chart with Heikin Ashi candles and RSI.
        Returns the image as a BytesIO buffer.
        """
        try:
            # Prepare Data (Last 50 periods for clarity)
            plot_df = df.tail(50).copy()

            # Create subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
            plt.subplots_adjust(hspace=0.0)

            # 1. Heikin Ashi Plot
            # Create a custom candle plot using bar charts for simplicity w/o external libs like mplfinance
            # Width of bars
            width = 0.6
            width2 = 0.1

            up = plot_df[plot_df['HA_Close'] >= plot_df['HA_Open']]
            down = plot_df[plot_df['HA_Close'] < plot_df['HA_Open']]

            # Plot Up Candles (Green)
            ax1.bar(up.index, up['HA_Close'] - up['HA_Open'], width, bottom=up['HA_Open'], color='green')
            ax1.bar(up.index, up['HA_High'] - up['HA_Close'], width2, bottom=up['HA_Close'], color='green')
            ax1.bar(up.index, up['HA_Low'] - up['HA_Open'], width2, bottom=up['HA_Open'], color='green')

            # Plot Down Candles (Red)
            ax1.bar(down.index, down['HA_Close'] - down['HA_Open'], width, bottom=down['HA_Open'], color='red')
            ax1.bar(down.index, down['HA_High'] - down['HA_Open'], width2, bottom=down['HA_Open'], color='red')
            ax1.bar(down.index, down['HA_Low'] - down['HA_Close'], width2, bottom=down['HA_Close'], color='red')

            # Add SMA 200 if available
            if 'SMA_200' in plot_df.columns:
                ax1.plot(plot_df.index, plot_df['SMA_200'], label='SMA 200', color='blue', linewidth=1.5)

            ax1.set_title(f"{ticker} - Heikin Ashi & RSI")
            ax1.set_ylabel("Price")
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # 2. RSI Plot
            ax2.plot(plot_df.index, plot_df['RSI'], label='RSI', color='purple')
            ax2.axhline(70, linestyle='--', color='red', alpha=0.5)
            ax2.axhline(30, linestyle='--', color='green', alpha=0.5)
            ax2.set_ylabel("RSI")
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            # Formatting Date Axis
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            plt.xticks(rotation=45)

            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close(fig)

            return buf

        except Exception as e:
            logger.error(f"Error generating chart for {ticker}: {e}")
            return None
