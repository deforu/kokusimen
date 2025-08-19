#!/usr/bin/env python3
"""
Raspberry Pi 5 メモリ監視ツール
メモリ使用量をリアルタイムで監視し、適切なWhisperモデルを推奨
"""

import psutil
import time
import os

def get_memory_info():
    """メモリ情報を取得"""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    return {
        'total_mb': memory.total // (1024 * 1024),
        'available_mb': memory.available // (1024 * 1024),
        'used_mb': memory.used // (1024 * 1024),
        'percent': memory.percent,
        'swap_total_mb': swap.total // (1024 * 1024),
        'swap_used_mb': swap.used // (1024 * 1024),
        'swap_percent': swap.percent
    }

def recommend_whisper_model(available_mb):
    """利用可能メモリに基づいてWhisperモデルを推奨"""
    if available_mb >= 3000:  # 3GB以上
        return "small", "高精度で使用可能"
    elif available_mb >= 1500:  # 1.5GB以上
        return "base", "推奨モデル"
    elif available_mb >= 800:   # 800MB以上
        return "tiny", "軽量モデル（最低限）"
    else:
        return None, "メモリ不足のため動作困難"

def display_memory_status():
    """メモリ状況を表示"""
    info = get_memory_info()
    
    print("=" * 60)
    print("🧠 Raspberry Pi 5 メモリ情報")
    print("=" * 60)
    print(f"総メモリ容量: {info['total_mb']:,} MB")
    print(f"使用中メモリ: {info['used_mb']:,} MB ({info['percent']:.1f}%)")
    print(f"利用可能メモリ: {info['available_mb']:,} MB")
    print()
    print(f"スワップ容量: {info['swap_total_mb']:,} MB")
    print(f"スワップ使用: {info['swap_used_mb']:,} MB ({info['swap_percent']:.1f}%)")
    print()
    
    # メモリ使用量バー
    bar_length = 40
    used_bars = int((info['percent'] / 100) * bar_length)
    memory_bar = "█" * used_bars + "░" * (bar_length - used_bars)
    print(f"メモリ使用量: [{memory_bar}] {info['percent']:.1f}%")
    
    # Whisperモデル推奨
    model, description = recommend_whisper_model(info['available_mb'])
    print()
    print("🎤 推奨Whisperモデル:")
    if model:
        print(f"   {model} - {description}")
    else:
        print(f"   {description}")
    
    print("=" * 60)

def monitor_memory_usage(interval=2):
    """メモリ使用量をリアルタイム監視"""
    print("リアルタイムメモリ監視を開始します (Ctrl+Cで終了)")
    print("=" * 60)
    
    try:
        while True:
            info = get_memory_info()
            
            # 使用量バー
            bar_length = 30
            used_bars = int((info['percent'] / 100) * bar_length)
            memory_bar = "█" * used_bars + "░" * (bar_length - used_bars)
            
            print(f"\rメモリ: [{memory_bar}] {info['percent']:5.1f}% "
                  f"({info['available_mb']:,}MB利用可能)", end="")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n監視を終了しました")

def check_whisper_requirements():
    """Whisperモデル別のメモリ要件をチェック"""
    info = get_memory_info()
    
    models = {
        'tiny': {'size_mb': 39, 'ram_mb': 500, 'description': '最軽量、速度重視'},
        'base': {'size_mb': 74, 'ram_mb': 1000, 'description': 'バランス重視'},
        'small': {'size_mb': 244, 'ram_mb': 2000, 'description': '精度重視'},
        'medium': {'size_mb': 769, 'ram_mb': 4000, 'description': '高精度'},
        'large': {'size_mb': 1550, 'ram_mb': 8000, 'description': '最高精度'}
    }
    
    print("🎤 Whisperモデル比較表")
    print("=" * 80)
    print(f"{'モデル':<8} {'サイズ':<10} {'必要RAM':<10} {'利用可否':<8} {'説明':<20}")
    print("-" * 80)
    
    for model, specs in models.items():
        can_use = "✅" if info['available_mb'] >= specs['ram_mb'] else "❌"
        print(f"{model:<8} {specs['size_mb']:>7}MB {specs['ram_mb']:>8}MB {can_use:<8} {specs['description']}")
    
    print("-" * 80)
    print(f"現在の利用可能メモリ: {info['available_mb']:,} MB")
    
    # 推奨モデル
    model, description = recommend_whisper_model(info['available_mb'])
    if model:
        print(f"推奨モデル: {model} ({description})")
    else:
        print(f"⚠️  {description}")

def free_memory():
    """メモリを解放する"""
    print("メモリ解放を試行中...")
    
    # Pythonのガベージコレクション実行
    import gc
    gc.collect()
    
    # システムキャッシュのクリア（要sudo権限）
    try:
        os.system("sudo sync")
        os.system("echo 1 | sudo tee /proc/sys/vm/drop_caches > /dev/null")
        print("✅ システムキャッシュをクリアしました")
    except:
        print("⚠️  システムキャッシュのクリアに失敗（sudo権限が必要）")
    
    # 結果表示
    time.sleep(1)
    info = get_memory_info()
    print(f"解放後の利用可能メモリ: {info['available_mb']:,} MB")

def main():
    """メイン関数"""
    print("🧠 Raspberry Pi 5 メモリ監視ツール")
    print("=" * 50)
    
    while True:
        print("\n選択してください:")
        print("1. メモリ状況表示")
        print("2. Whisperモデル要件チェック")
        print("3. リアルタイムメモリ監視")
        print("4. メモリ解放")
        print("5. 終了")
        
        choice = input("選択 (1-5): ").strip()
        
        if choice == "1":
            display_memory_status()
        elif choice == "2":
            check_whisper_requirements()
        elif choice == "3":
            monitor_memory_usage()
        elif choice == "4":
            free_memory()
        elif choice == "5":
            print("プログラムを終了します")
            break
        else:
            print("無効な選択です")

if __name__ == "__main__":
    main()