import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression, BayesianRidge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
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
    st.sidebar.dataframe(data.head(), use_container_width=True)

    # 选择筛选条件
    filter_column = st.sidebar.selectbox("选择筛选列", data.columns)
    unique_values = data[filter_column].unique()
    filter_value = st.sidebar.selectbox("选择筛选值", unique_values)

    # 筛选数据
    filtered_data = data[data[filter_column] == filter_value]

    st.sidebar.write("筛选后的数据预览：")
    st.sidebar.dataframe(filtered_data.head(), use_container_width=True)

    # 选择特征变量
    features = st.sidebar.multiselect("选择自变量", filtered_data.select_dtypes(include=[np.number]).columns)

    # 选择目标变量
    target = st.sidebar.selectbox("选择应变量", [""] + list(filtered_data.columns))

    # 选择算法类型
    algorithms = st.sidebar.multiselect(
        "选择算法类型",
        ["线性回归", "贝叶斯回归", "随机森林", "LSTM", "决策树回归", "梯度提升回归"]
    )

    if target and target != "" and features and algorithms:
        X = filtered_data[features]
        y = filtered_data[target]

        # 处理缺失值
        imputer = SimpleImputer(strategy='mean')
        X = imputer.fit_transform(X)
        y = imputer.fit_transform(y.values.reshape(-1, 1)).ravel()

        # 标准化数据
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 创建模型结果展示的列布局
        cols = st.columns(len(algorithms))

        models = {}

        for i, algorithm in enumerate(algorithms):
            with cols[i]:
                if algorithm == "线性回归":
                    model = LinearRegression()
                elif algorithm == "贝叶斯回归":
                    model = BayesianRidge()
                elif algorithm == "随机森林":
                    # 使用 GridSearchCV 调整超参数
                    param_grid = {
                        'n_estimators': [50, 100, 200],
                        'max_depth': [None, 10, 20, 30],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4]
                    }
                    rf = RandomForestRegressor(random_state=42)
                    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2)
                    grid_search.fit(X_train, y_train)
                    model = grid_search.best_estimator_
                elif algorithm == "决策树回归":
                    model = DecisionTreeRegressor()
                elif algorithm == "梯度提升回归":
                    model = GradientBoostingRegressor()
                elif algorithm == "LSTM":
                    y_train_lstm = y_train.reshape(-1, 1)
                    y_test_lstm = y_test.reshape(-1, 1)
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
                    y_test_np = y_test  # 将 y_test 转换为 NumPy 数组
                    results = pd.DataFrame({"实际值": y_test_np[3:].flatten(), "预测值": predictions.flatten()})
                    st.dataframe(results, use_container_width=True)
                    mse = mean_squared_error(y_test_np[3:], predictions)
                    rmse = math.sqrt(mse)
                    variance = np.var(predictions)
                    st.write(f"MSE: {mse:.2f}")
                    st.write(f"RMSE: {rmse:.2f}")
                    st.write(f"预测结果的方差: {variance:.2f}")
                    models["LSTM"] = model
                    continue

                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
                st.write(algorithm)
                results = pd.DataFrame(X_test, columns=features)
                results["实际值"] = y_test
                results["预测值"] = predictions
                st.dataframe(results, use_container_width=True)
                variance = np.var(predictions)
                st.write(f"预测结果的方差: {variance:.2f}")
                models[algorithm] = model

        # 增加特征变量手工输入框
        st.sidebar.write("调整特征变量值进行预测")
        feature_values = {}
        for feature in features:
            mean_value = float(filtered_data[feature].mean())

            # 初始化 session_state
            if f"{feature}_input" not in st.session_state:
                st.session_state[f"{feature}_input"] = f"{mean_value:.2f}"

            # 手工输入调整
            input_value = st.sidebar.text_input(
                f"{feature} (手工输入)",
                key=f"{feature}_input"
            )

            feature_values[feature] = float(st.session_state[f"{feature}_input"])

        # 创建一个包含手工输入值的 DataFrame
        future_data = pd.DataFrame([feature_values])

        # 进行结果预测
        future_cols = st.columns(len(algorithms))
        for i, algorithm in enumerate(algorithms):
            with future_cols[i]:
                if algorithm in models:
                    model = models[algorithm]
                    if algorithm == "LSTM":
                        last_data = y_train_lstm[-3:]  # 使用最后3天的数据作为输入
                        future_predictions = []
                        for _ in range(len(future_data)):
                            input_data = last_data.reshape((1, 3, 1))
                            prediction = model.predict(input_data)
                            future_predictions.append(prediction[0, 0])
                            last_data = np.append(last_data[1:], prediction)
                        future_data["预测值"] = future_predictions
                    else:
                        future_predictions = model.predict(future_data[features])  # 确保使用相同的特征集
                        future_data["预测值"] = future_predictions

                    st.write(f"{algorithm} 未来预测")
                    st.dataframe(future_data, use_container_width=True)
                else:
                    st.write(f"{algorithm} 不支持未来预测")
    else:
        st.sidebar.error("请确保选择了应变量、自变量和算法类型")