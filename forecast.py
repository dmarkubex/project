import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, GRU
from sklearn.metrics import mean_squared_error
import math
import matplotlib.pyplot as plt

# 设置中文字体以避免乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False

# 标题
st.title("预测模型应用")

# 使用 sidebar 创建侧边栏
with st.sidebar:
    # 上传数据文件
    uploaded_file = st.file_uploader("上传一个CSV或Excel文件", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # 读取数据文件
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.sidebar.write("数据预览：")
    st.sidebar.write(data.head())

    # 选择目标变量
    target = st.sidebar.selectbox("选择目标变量", data.columns)

    # 选择特征变量
    features = st.sidebar.multiselect("选择特征变量", data.select_dtypes(include=[np.number]).columns)

    # 选择算法类型
    algorithms = st.sidebar.multiselect(
        "选择算法类型",
        ["线性回归", "随机森林", "支持向量机", "LSTM", "决策树回归", "梯度提升回归", "XGBoost", "LightGBM", "CatBoost", "GRU"]
    )

    if target and features and algorithms:
        X = data[features]
        y = data[target]

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 创建模型结果展示的列布局
        cols = st.columns(len(algorithms))

        models = {}

        for i, algorithm in enumerate(algorithms):
            with cols[i]:
                if algorithm == "线性回归":
                    model = LinearRegression()
                elif algorithm == "随机森林":
                    model = RandomForestRegressor(n_estimators=100)
                elif algorithm == "支持向量机":
                    model = SVR()
                elif algorithm == "决策树回归":
                    model = DecisionTreeRegressor()
                elif algorithm == "梯度提升回归":
                    model = GradientBoostingRegressor()
                elif algorithm == "XGBoost":
                    model = xgb.XGBRegressor()
                elif algorithm == "LightGBM":
                    model = lgb.LGBMRegressor()
                elif algorithm == "CatBoost":
                    model = CatBoostRegressor(verbose=0)
                elif algorithm == "LSTM":
                    y_train_lstm = y_train.values.reshape(-1, 1)
                    y_test_lstm = y_test.values.reshape(-1, 1)
                    X_train_lstm, y_train_lstm_seq = [], []
                    for i in range(3, len(y_train_lstm)):
                        X_train_lstm.append(y_train_lstm[i-3:i, 0])
                        y_train_lstm_seq.append(y_train_lstm[i, 0])
                    X_train_lstm, y_train_lstm_seq = np.array(X_train_lstm), np.array(y_train_lstm_seq)
                    X_train_lstm = np.reshape(X_train_lstm, (X_train_lstm.shape[0], X_train_lstm.shape[1], 1))

                    model = Sequential()
                    model.add(LSTM(50, activation='relu', input_shape=(3, 1)))
                    model.add(Dense(1))
                    model.compile(optimizer='adam', loss='mse')
                    model.fit(X_train_lstm, y_train_lstm_seq, epochs=200, verbose=0)

                    X_test_lstm = []
                    for i in range(3, len(y_test_lstm)):
                        X_test_lstm.append(y_test_lstm[i-3:i, 0])
                    X_test_lstm = np.array(X_test_lstm)
                    X_test_lstm = np.reshape(X_test_lstm, (X_test_lstm.shape[0], X_test_lstm.shape[1], 1))

                    predictions = model.predict(X_test_lstm)
                    st.write("LSTM")
                    y_test_np = y_test.values  # 将 y_test 转换为 NumPy 数组
                    results = pd.DataFrame({"实际值": y_test_np[3:].flatten(), "预测值": predictions.flatten()})
                    st.write(results)
                    mse = mean_squared_error(y_test_np[3:], predictions)
                    rmse = math.sqrt(mse)
                    st.write(f"MSE: {mse:.2f}")
                    st.write(f"RMSE: {rmse:.2f}")
                    models["LSTM"] = model
                    continue
                elif algorithm == "GRU":
                    y_train_gru = y_train.values.reshape(-1, 1)
                    y_test_gru = y_test.values.reshape(-1, 1)
                    X_train_gru, y_train_gru_seq = [], []
                    for i in range(3, len(y_train_gru)):
                        X_train_gru.append(y_train_gru[i-3:i, 0])
                        y_train_gru_seq.append(y_train_gru[i, 0])
                    X_train_gru, y_train_gru_seq = np.array(X_train_gru), np.array(y_train_gru_seq)
                    X_train_gru = np.reshape(X_train_gru, (X_train_gru.shape[0], X_train_gru.shape[1], 1))

                    model = Sequential()
                    model.add(GRU(50, activation='relu', input_shape=(3, 1)))
                    model.add(Dense(1))
                    model.compile(optimizer='adam', loss='mse')
                    model.fit(X_train_gru, y_train_gru_seq, epochs=200, verbose=0)

                    X_test_gru = []
                    for i in range(3, len(y_test_gru)):
                        X_test_gru.append(y_test_gru[i-3:i, 0])
                    X_test_gru = np.array(X_test_gru)
                    X_test_gru = np.reshape(X_test_gru, (X_test_gru.shape[0], X_test_gru.shape[1], 1))

                    predictions = model.predict(X_test_gru)
                    st.write("GRU")
                    y_test_np = y_test.values  # 将 y_test 转换为 NumPy 数组
                    results = pd.DataFrame({"实际值": y_test_np[3:].flatten(), "预测值": predictions.flatten()})
                    st.write(results)
                    mse = mean_squared_error(y_test_np[3:], predictions)
                    rmse = math.sqrt(mse)
                    st.write(f"MSE: {mse:.2f}")
                    st.write(f"RMSE: {rmse:.2f}")
                    models["GRU"] = model
                    continue

                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
                st.write(algorithm)
                results = pd.DataFrame(X_test, columns=features)
                results["实际值"] = y_test.values
                results["预测值"] = predictions
                st.write(results)
                st.write(f"R^2: {model.score(X_test, y_test):.2f}")
                models[algorithm] = model

        # 增加特征变量滑动块
        st.sidebar.write("调整特征变量值进行预测")
        feature_values = {}
        for feature in features:
            min_value = float(data[feature].min())
            max_value = float(data[feature].max())
            mean_value = float(data[feature].mean())
            feature_values[feature] = st.sidebar.slider(f"{feature}", min_value, max_value, mean_value)

        # 创建一个包含滑动块值的 DataFrame
        future_data = pd.DataFrame([feature_values])

        # 进行结果预测
        future_cols = st.columns(len(algorithms))
        for i, algorithm in enumerate(algorithms):
            with future_cols[i]:
                if algorithm in models:
                    model = models[algorithm]
                    if algorithm == "LSTM" or algorithm == "GRU":
                        last_data = y_train_lstm[-3:] if algorithm == "LSTM" else y_train_gru[-3:]  # 使用最后3天的数据作为输入
                        future_predictions = []
                        for _ in range(len(future_data)):
                            input_data = last_data.reshape((1, 3, 1))
                            prediction = model.predict(input_data)
                            future_predictions.append(prediction[0, 0])
                            last_data = np.append(last_data[1:], prediction)
                        future_data["预测值"] = future_predictions
                    else:
                        future_predictions = model.predict(future_data)
                        future_data["预测值"] = future_predictions

                    st.write(f"{algorithm} 未来预测")
                    st.write(future_data)
                else:
                    st.write(f"{algorithm} 不支持未来预测")