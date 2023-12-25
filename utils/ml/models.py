import tensorflow as tf
from sklearn.ensemble import RandomForestRegressor


def get_ML1(input_shape, optimizer, loss, metrics):
    """Create the ML1 model

    Args:
        input_shape (tuple): shape of the input data
        optimizer (str): optimizer to use
        loss (str): loss function to use
        metrics (list): list of metrics to use

    Returns:
        tf.keras.Model: ML1 model
    """

    input = tf.keras.Input(shape=input_shape)
    x = tf.keras.layers.Dense(8, activation="relu")(input)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(
        64,
    )(input)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(8, activation="relu")(x)
    output = tf.keras.layers.Dense(1, activation="relu")(x)

    model = tf.keras.Model(inputs=input, outputs=output)
    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    return model


def get_ML1RF(
    n_estimators=100, criterion="squared_error", max_depth=None, random_state=None
):
    """
    Create random forest regressor model

    Args:
        n_estimators (int): number of trees in the forest
        criterion (str): function to measure the quality of a split
        max_depth (int): maximum depth of the tree
        random_state (int): controls both the randomness of the bootstrapping of the samples used when building trees
                            and the sampling of the features to consider when looking for the best split at each node.

    Returns:
        RandomForestRegressor: ML1RF model
    """

    model = RandomForestRegressor(
        n_estimators=n_estimators,
        criterion=criterion,
        max_depth=max_depth,
        random_state=random_state,
    )

    return model


class CoreBlock(tf.keras.layers.Layer):
    def __init__(self):
        super().__init__()
        self.layer1 = tf.keras.layers.Dense(16, activation="relu")
        self.layer2 = tf.keras.layers.Dense(64)
        self.layer3 = tf.keras.layers.Dense(64)
        self.layer4 = tf.keras.layers.Dense(16, activation="relu")
        self.layer5 = tf.keras.layers.Dense(1, activation="relu")
        # TODO: add dropout and batch normalization

    def call(self, inputs):
        x = self.layer1(inputs)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        output = self.layer5(x)

        return output

class Stage1(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.block1 = CoreBlock()

    def call(self, inputs):
        res1 = tf.keras.layers.Dense(8)(inputs)
        x = self.block1(res1)

        return x

class ML1(tf.keras.Model):
    def __init__(self):
        super().__init__()
        self.block1 = CoreBlock()
        self.block2 = CoreBlock()

    def call(self, inputs):
        res1 = tf.keras.layers.Dense(8)(inputs)
        x = self.block1(res1)
        x = tf.keras.layers.add([x, res1])
        x = self.block2(x)

        return x