import keras

import tensorflow as tf
from tensorflow.python.platform import app
from tensorflow.python.platform import flags

from utils_mnist import data_mnist, model_mnist
from utils_tf import tf_model_train, tf_model_eval
from attacks import fgsm

FLAGS = flags.FLAGS

flags.DEFINE_string('train_dir', '/tmp', 'Directory storing the saved model.')
flags.DEFINE_string('filename', 'mnist.ckpt', 'Filename to save model under.')
flags.DEFINE_integer('nb_epochs', 6, 'Number of epochs to train model')
flags.DEFINE_integer('batch_size', 128, 'Size of training batches')
flags.DEFINE_integer('nb_classes', 10, 'Number of classification classes')
flags.DEFINE_integer('img_rows', 28, 'Input row dimension')
flags.DEFINE_integer('img_cols', 28, 'Input column dimension')
flags.DEFINE_integer('nb_filters', 64, 'Number of convolutional filter to use')
flags.DEFINE_integer('nb_pool', 2, 'Size of pooling area for max pooling')
flags.DEFINE_float('learning_rate', 0.1, 'Learning rate for training')


def main(argv=None):
    """
    MNIST cleverhans tutorial
    :return:
    """

    # Create TF session and set as Keras backend session
    sess = tf.Session()
    keras.backend.set_session(sess)
    print "Created TensorFlow session and set Keras backend."

    # Get MNIST test data
    X_train, Y_train, X_test, Y_test = data_mnist()
    print "Loaded MNIST test data."

    # Define input TF placeholder
    x = tf.placeholder(tf.float32, shape=(FLAGS.batch_size, 1, 28, 28))
    y = tf.placeholder(tf.float32, shape=(FLAGS.batch_size, FLAGS.nb_classes))

    # Define TF model graph
    model = model_mnist(x)
    print "Defined TensorFlow model graph."

    # Train a MNIST model
    tf_model_train(sess, x, y, model, X_train, Y_train)

    # Evaluate the accuracy of the MNIST model on legitimate test examples
    accuracy = tf_model_eval(sess, x, y, model, X_test, Y_test)
    print 'Test accuracy on legitimate test examples: ' + str(accuracy)

    # Craft adversarial examples using Fast Gradient Sign Method (FGSM)
    adv_ex = fgsm(sess, x, y, model, X_test, Y_test, eps=0.3)

    # Evaluate the accuracy of the MNIST model on adversarial examples
    accuracy = tf_model_eval(sess, x, y, model, adv_ex, Y_test)
    print'Test accuracy on adversarial examples: ' + str(accuracy)

    # Redefine TF model graph
    model_adv = model_mnist(x)

    # Perform adversarial training
    tf_model_train(sess, x, y, model_adv, X_train, Y_train, adversarial=True)

    # Craft adversarial examples using Fast Gradient Sign Method (FGSM) on
    # the new model, which was trained using adversarial training
    adv_ex_2 = fgsm(sess, x, y, model_adv, X_test, Y_test, eps=0.3)

    # Evaluate the accuracy of the adversarially trained MNIST model on
    # adversarial examples
    accuracy_adv = tf_model_eval(sess, x, y, model_adv, adv_ex_2, Y_test)
    print'Test accuracy on adversarial examples: ' + str(accuracy_adv)


if __name__ == '__main__':
    app.run()
