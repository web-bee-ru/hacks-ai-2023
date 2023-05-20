import numpy as np
from keras import callbacks
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

class MetricsCallback(callbacks.Callback):
    def __init__(self, x_train, y_train, x_val, y_val):
        self.x_train = x_train
        self.y_train = y_train
        self.x_val = x_val
        self.y_val = y_val

    def on_train_begin(self, logs=None):
        self.f1s = []
        self.val_f1s = []
        # self.val_recalls = []
        # self.val_precisions = []

    def on_epoch_end(self, epoch, logs=None):
        train_predict = (np.asarray(self.model.predict(self.x_train))).round()
        train_targ = self.y_train
        f1 = f1_score(train_targ, train_predict, average='macro')
        self.f1s.append(f1)

        val_predict = (np.asarray(self.model.predict(self.x_val))).round()
        val_targ = self.y_val
        val_f1 = f1_score(val_targ, val_predict, average='macro')
        self.val_f1s.append(val_f1)
        # val_recall = recall_score(val_targ, val_predict, average='macro')
        # self.val_recalls.append(val_recall)
        # val_precision = precision_score(val_targ, val_predict, average='macro')
        # self.val_precisions.append(val_precision)
        print("— f1: %f, val f1: %f" % (f1, val_f1))
