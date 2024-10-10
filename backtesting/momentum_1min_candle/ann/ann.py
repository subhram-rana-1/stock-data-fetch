from pandas import read_csv, DataFrame
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.src.models import Sequential
from keras.src.layers import Dense
from typing import List

from backtesting.momentum_1min_candle.ann.data_gen import Input


def get_input_output_dataset(relative_file_path: str) -> (DataFrame, DataFrame):
    df = read_csv(relative_file_path)

    input = df[Input.dataset_input_headers]
    output = df[Input.dataset_output_headers]

    print(input.head())
    print(output.head())

    return input, output


def compare_test_dataset_result_with_real_output(
        ANN,
        normalised_input_test,
        real_output_test,
) -> List[List[int]]:
    confusion_matrix: List[List[int]] = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]

    predicted_output_test = ANN.predict(normalised_input_test)

    i = 0
    while i < len(predicted_output_test):
        predicted = predicted_output_test[i]
        real = real_output_test.iloc[i].values

        real_idx, predicted_idx = None, None

        if real[0] == 1: real_idx = 0
        elif real[1] == 1: real_idx = 1
        elif real[2] == 1: real_idx = 2

        if predicted[0] >= 0.9: predicted_idx = 0
        elif predicted[1] >= 0.9: predicted_idx = 1
        elif predicted[2] >= 0.9: predicted_idx = 2

        if predicted_idx is not None:
            confusion_matrix[real_idx][predicted_idx] += 1

        i += 1

    return confusion_matrix


def main():
    input, output = get_input_output_dataset(Input.dataset_file_path)

    input_train, input_test, output_train, output_test = \
        train_test_split(input, output, test_size=0.2, random_state=20)

    input_scaler = StandardScaler().fit(input)

    normalised_input_train = input_scaler.transform(input_train)
    normalised_input_test = input_scaler.transform(input_test)

    ANN = Sequential()

    # ----- linear feed-forward ANN model -----
    # ANN.add(Dense(1, input_dim=2, activation='linear', name='output_layer'))  # linear model

    # ----- nonlinear feed-forward ANN model -----
    ANN.add(Dense(50, input_dim=9, activation='relu', name='hidden_1'))
    ANN.add(Dense(50, activation='relu', name='hidden_2'))
    ANN.add(Dense(50, activation='relu', name='hidden_3'))
    ANN.add(Dense(50, activation='relu', name='hidden_4'))
    ANN.add(Dense(50, activation='relu', name='hidden_5'))
    ANN.add(Dense(3, activation='relu', name='output_layer'))

    ANN.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae'])
    ANN.summary()

    ANN.fit(normalised_input_train, output_train, validation_split=0.2, epochs=100)

    # ---- post training evaluation --
    normalised_input_test = input_scaler.transform(input_test)
    mean_squared_error, mean_absolute_error = ANN.evaluate(normalised_input_test, output_test)
    print(f'mean_squared_error: {mean_squared_error}')
    print(f'mean_absolute_error: {mean_absolute_error}')
    # --------------------------------

    confusion_matrix = compare_test_dataset_result_with_real_output(
        ANN,
        normalised_input_test,
        output_test,
    )

    print(f'confusion_matrix: \n {confusion_matrix}')


# --------- confusion matrix for the last run
#                predicted
#
#              59, 126,  46
#   real ->    58, 1434, 41
#              41, 103,  53
# ------------------------------------------
