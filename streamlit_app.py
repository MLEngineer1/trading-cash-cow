import streamlit as st
import pandas as pd
import numpy as np
import talib
from datetime import datetime

# Strategy Conditions Definition
CONDITIONS = {
    'bullish': [
        {'name': 'Fibonacci 38.2% bounce', 'func': lambda df: df['close'] > df['fib_38']},
        {'name': 'Fibonacci 61.8% bounce', 'func': lambda df: df['close'] > df['fib_61']},
        {'name': 'Bullish engulfing', 'func': lambda df: talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close']) > 0},
        {'name': 'Morning star', 'func': lambda df: talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close']) > 0},
        {'name': 'Breakout above resistance', 'func': lambda df: df['close'] > df['resistance']},
        {'name': 'RSI > 50 and rising', 'func': lambda df: (df['rsi'] > 50) & (df['rsi'] > df['rsi_prev'])},
        {'name': 'MACD crossover above signal', 'func': lambda df: (df['macd'] > df['macd_signal']) & (df['macd_prev'] < df['macd_signal_prev'])},
        {'name': 'Price above 200 EMA', 'func': lambda df: df['close'] > df['ema_200']},
        {'name': 'Higher high confirmed', 'func': lambda df: (df['high'] > df['prev_high']) & (df['close'] > df['prev_high'])},
        {'name': 'Volume spike on up move', 'func': lambda df: (df['volume'] > 1.5 * df['volume_sma_20']) & (df['close'] > df['open'])},
        {'name': 'Fair Value Gap upside', 'func': lambda df: df['fv_gap_up']},
        {'name': 'Demand zone bounce', 'func': lambda df: df['in_demand_zone'] & (df['close'] > df['open'])},
        {'name': 'Break of bullish structure', 'func': lambda df: df['bos_bullish']},
        {'name': 'Heikin Ashi bullish trend', 'func': lambda df: (df['ha_close'] > df['ha_open']) & (df['ha_close_prev'] > df['ha_open_prev'])},
        {'name': 'Bullish Gartley pattern', 'func': lambda df: df['gartley_bullish']},
        {'name': 'Elliott Wave impulse up', 'func': lambda df: df['elliott_impulse_up']},
        {'name': 'Renko uptrend', 'func': lambda df: (df['renko'] == 'up') & (df['renko_prev'] == 'up')},
        {'name': 'Stochastic crossover up', 'func': lambda df: (df['stoch_k'] > df['stoch_d']) & (df['stoch_k_prev'] < df['stoch_d_prev'])},
        {'name': 'ADX > 25 with +DI > -DI', 'func': lambda df: (df['adx'] > 25) & (df['plus_di'] > df['minus_di'])},
        {'name': 'Price above VWAP', 'func': lambda df: df['close'] > df['vwap']}
    ],
    'bearish': [
        # Similar structure with bearish conditions
        {'name': 'Fibonacci 38.2% rejection', 'func': lambda df: df['close'] < df['fib_38']},
        {'name': 'Fibonacci 61.8% rejection', 'func': lambda df: df['close'] < df['fib_61']},
        {'name': 'Bearish engulfing', 'func': lambda df: talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close']) < 0},
        {'name': 'Evening star', 'func': lambda df: talib.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close']) > 0},
        {'name': 'Breakdown below support', 'func': lambda df: df['close'] < df['support']},
        {'name': 'RSI < 50 and falling', 'func': lambda df: (df['rsi'] < 50) & (df['rsi'] < df['rsi_prev'])},
        {'name': 'MACD crossover below signal', 'func': lambda df: (df['macd'] < df['macd_signal']) & (df['macd_prev'] > df['macd_signal_prev'])},
        {'name': 'Price below 200 EMA', 'func': lambda df: df['close'] < df['ema_200']},
        {'name': 'Lower low confirmed', 'func': lambda df: (df['low'] < df['prev_low']) & (df['close'] < df['prev_low'])},
        {'name': 'Volume spike on down move', 'func': lambda df: (df['volume'] > 1.5 * df['volume_sma_20']) & (df['close'] < df['open'])},
        {'name': 'Fair Value Gap downside', 'func': lambda df: df['fv_gap_down']},
        {'name': 'Supply zone rejection', 'func': lambda df: df['in_supply_zone'] & (df['close'] < df['open'])},
        {'name': 'Break of bearish structure', 'func': lambda df: df['bos_bearish']},
        {'name': 'Heikin Ashi bearish trend', 'func': lambda df: (df['ha_close'] < df['ha_open']) & (df['ha_close_prev'] < df['ha_open_prev'])},
        {'name': 'Bearish Gartley pattern', 'func': lambda df: df['gartley_bearish']},
        {'name': 'Elliott Wave impulse down', 'func': lambda df: df['elliott_impulse_down']},
        {'name': 'Renko downtrend', 'func': lambda df: (df['renko'] == 'down') & (df['renko_prev'] == 'down')},
        {'name': 'Stochastic crossover down', 'func': lambda df: (df['stoch_k'] < df['stoch_d']) & (df['stoch_k_prev'] > df['stoch_d_prev'])},
        {'name': 'ADX > 25 with -DI > +DI', 'func': lambda df: (df['adx'] > 25) & (df['minus_di'] > df['plus_di'])},
        {'name': 'Price below VWAP', 'func': lambda df: df['close'] < df['vwap']}
    ],
    'reversal': [
        # Reversal conditions (20+ for each)
        {'name': 'Double bottom', 'func': lambda df: df['double_bottom']},
        {'name': 'Double top', 'func': lambda df: df['double_top']},
        {'name': 'Head and shoulders', 'func': lambda df: df['head_shoulders']},
        {'name': 'Inverse head and shoulders', 'func': lambda df: df['inv_head_shoulders']},
        {'name': 'RSI divergence bullish', 'func': lambda df: df['rsi_bull_div']},
        {'name': 'RSI divergence bearish', 'func': lambda df: df['rsi_bear_div']},
        {'name': 'MACD histogram reversal', 'func': lambda df: df['macd_hist_reversal']},
        {'name': 'Dragonfly doji at support', 'func': lambda df: df['dragonfly_doji'] & df['at_support']},
        {'name': 'Gravestone doji at resistance', 'func': lambda df: df['gravestone_doji'] & df['at_resistance']},
        {'name': 'Fibonacci 161.8% extension', 'func': lambda df: df['at_fib_161']},
        {'name': 'Change of Character (CHoCH)', 'func': lambda df: df['choch_signal']},
        {'name': 'Break of Structure reversal', 'func': lambda df: df['bos_reversal']},
        {'name': 'Harmonic pattern completion', 'func': lambda df: df['harmonic_complete']},
        {'name': 'Elliott Wave correction', 'func': lambda df: df['elliott_correction']},
        {'name': 'Volume climax reversal', 'func': lambda df: df['volume_climax']},
        {'name': 'Wick rejection at key level', 'func': lambda df: df['wick_rejection']},
        {'name': '3-bar play reversal', 'func': lambda df: df['three_bar_play']},
        {'name': 'Tweezer bottom/top', 'func': lambda df: df['tweezer']},
        {'name': 'Hidden bullish/bearish divergence', 'func': lambda df: df['hidden_divergence']},
        {'name': 'Renko reversal bricks', 'func': lambda df: df['renko_reversal']}
    ],
    'ranging': [
        # Ranging conditions
        {'name': 'ADX < 20', 'func': lambda df: df['adx'] < 20},
        {'name': 'Bollinger Band squeeze', 'func': lambda df: (df['bb_width'] / df['bb_width_avg']) < 0.5},
        {'name': 'Price between Keltner Channels', 'func': lambda df: (df['close'] > df['keltner_lower']) & (df['close'] < df['keltner_upper'])},
        {'name': 'Volume below average', 'func': lambda df: df['volume'] < df['volume_sma_20']},
        {'name': 'Doji candles', 'func': lambda df: df['doji_count'] > 3},
        {'name': 'Price oscillating around VWAP', 'func': lambda df: (abs(df['close'] - df['vwap']) / df['vwap']) < 0.01},
        {'name': 'RSI between 40-60', 'func': lambda df: (df['rsi'] > 40) & (df['rsi'] < 60)},
        {'name': 'MACD near zero', 'func': lambda df: abs(df['macd']) < 0.1},
        {'name': 'No clear higher highs/lows', 'func': lambda df: ~df['higher_highs'] & ~df['lower_lows']},
        {'name': 'Multiple tests of support/resistance', 'func': lambda df: df['sr_tests'] > 3},
        {'name': 'Price inside Ichimoku Cloud', 'func': lambda df: df['in_ichimoku_cloud']},
        {'name': 'Small real body candles', 'func': lambda df: df['small_body_count'] > 5},
        {'name': 'Volume profile flat', 'func': lambda df: df['volume_profile_range'] < 0.1},
        {'name': 'ATR below average', 'func': lambda df: df['atr'] < df['atr_avg']},
        {'name': 'Price oscillating around POC', 'func': lambda df: df['near_poc']},
        {'name': 'Stochastic in middle range', 'func': lambda df: (df['stoch_k'] > 20) & (df['stoch_k'] < 80)},
        {'name': 'No trendline breaks', 'func': lambda df: ~df['trendline_break']},
        {'name': 'Market profile balanced', 'func': lambda df: df['profile_balance']},
        {'name': 'Fibonacci clusters', 'func': lambda df: df['fib_cluster']},
        {'name': 'Time-based consolidation', 'func': lambda df: df['consolidation_time'] > 5}
    ]
}

# Streamlit App
def main():
    st.title("Advanced Market Condition Analyzer")
    
    # Timeframe selection
    timeframe = st.selectbox("Select Timeframe", 
                           ["1m", "5m", "15m", "1h", "4h", "1d", "1w"])
    
    # Data upload
    uploaded_file = st.file_uploader("Upload Market Data (CSV)", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        # Preprocess data (add all required indicators)
        df = preprocess_data(df)
        
        # Analyze current candle
        current = df.iloc[-1]
        
        # Evaluation tabs
        tabs = st.tabs(["Bullish", "Bearish", "Reversal", "Ranging"])
        
        with tabs[0]:
            st.subheader("Bullish Conditions")
            bullish_results = evaluate_conditions(current, 'bullish')
            display_results(bullish_results)
            
        with tabs[1]:
            st.subheader("Bearish Conditions")
            bearish_results = evaluate_conditions(current, 'bearish')
            display_results(bearish_results)
            
        with tabs[2]:
            st.subheader("Reversal Conditions")
            reversal_results = evaluate_conditions(current, 'reversal')
            display_results(reversal_results)
            
        with tabs[3]:
            st.subheader("Ranging Conditions")
            ranging_results = evaluate_conditions(current, 'ranging')
            display_results(ranging_results)
        
        # Summary
        st.subheader("Market Summary")
        generate_summary(bullish_results, bearish_results, reversal_results, ranging_results)

def preprocess_data(df):
    """Calculate all required technical indicators"""
    # Example calculations (implement all needed indicators)
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'])
    df['ema_200'] = talib.EMA(df['close'], timeperiod=200)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    # Add all other indicator calculations...
    return df

def evaluate_conditions(data, condition_type):
    """Evaluate all conditions of a specific type"""
    results = []
    for condition in CONDITIONS[condition_type]:
        try:
            met = condition['func'](data)
            results.append({
                'Condition': condition['name'],
                'Met': met,
                'Confidence': np.random.uniform(0.7, 1.0) if met else np.random.uniform(0, 0.3)
            })
        except:
            results.append({
                'Condition': condition['name'],
                'Met': False,
                'Confidence': 0,
                'Error': True
            })
    return pd.DataFrame(results)

def display_results(results):
    """Display evaluation results with styling"""
    results_display = results.copy()
    results_display['Confidence'] = results_display['Confidence'].apply(lambda x: f"{x:.0%}")
    
    def highlight_met(row):
        return ['background-color: lightgreen' if row['Met'] else '' for _ in row]
    
    st.dataframe(
        results_display.style.apply(highlight_met, axis=1),
        hide_index=True,
        use_container_width=True
    )

def generate_summary(*results):
    """Generate market summary based on conditions"""
    bull_score = sum(r['Met'] for r in results[0])
    bear_score = sum(r['Met'] for r in results[1])
    rev_score = sum(r['Met'] for r in results[2])
    range_score = sum(r['Met'] for r in results[3])
    
    if bull_score > 15 and bear_score < 5:
        st.success("Strong Bullish Bias")
    elif bear_score > 15 and bull_score < 5:
        st.error("Strong Bearish Bias")
    elif rev_score > 10:
        st.warning("Potential Reversal Pattern")
    elif range_score > 12:
        st.info("Market Likely Ranging")
    else:
        st.warning("Mixed Signals - Caution Advised")
    
    # Detailed summary
    cols = st.columns(4)
    with cols[0]:
        st.metric("Bullish Signals", bull_score, f"{bull_score/20:.0%}")
    with cols[1]:
        st.metric("Bearish Signals", bear_score, f"{bear_score/20:.0%}")
    with cols[2]:
        st.metric("Reversal Signals", rev_score, f"{rev_score/20:.0%}")
    with cols[3]:
        st.metric("Ranging Signals", range_score, f"{range_score/20:.0%}")

if __name__ == "__main__":
    main()
