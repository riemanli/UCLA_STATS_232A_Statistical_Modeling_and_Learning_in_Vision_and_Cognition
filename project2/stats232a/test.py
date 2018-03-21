from __future__ import print_function
import time
import numpy as np
import matplotlib.pyplot as plt
from stats232a.classifiers.fc_net import *
from stats232a.data_utils import *
from stats232a.gradient_check import eval_numerical_gradient, eval_numerical_gradient_array
from stats232a.solver import Solver
from stats232a.layers import *


def rel_error(x, y):
    """ returns relative error """
    return np.max(np.abs(x - y) / (np.maximum(1e-8, np.abs(x) + np.abs(y))))

# load CIFAR-10 dataset
# from stats232a.data_utils import get_CIFAR10_data
# data = get_CIFAR10_data()
# for k, v in list(data.items()):
#     print(('%s: ' % k, v.shape))


class Test(object):
    def __init__(self):
        # Load the (preprocessed) MNIST data.
        # The second dimension of images indicated the number of channel. For black and white images in MNIST, channel=1.
        # Load the raw MNIST data
        num_training = 59000
        num_validation = 1000
        num_test = 1000
        subtract_mean = True

        mnist_dir = '/home/parallels/PycharmProjects/Courses/232A/project2/stats232a/datasets'
        X_train, y_train = load_mnist(dataset="training", path=mnist_dir, size=num_training + num_validation)
        X_test, y_test = load_mnist(dataset="testing", path=mnist_dir, size=num_test)

        # Subsample the data
        mask = list(range(num_training, num_training + num_validation))
        X_val = X_train[mask]
        y_val = y_train[mask]
        mask = list(range(num_training))
        X_train = X_train[mask]
        y_train = y_train[mask]

        # Normalize the data: subtract the mean image
        if subtract_mean:
            mean_image = np.mean(X_train, axis=0)
            X_train -= mean_image
            X_val -= mean_image
            X_test -= mean_image

        # Transpose so that channels come first
        X_train = X_train.transpose(0, 3, 1, 2).copy()
        X_val = X_val.transpose(0, 3, 1, 2).copy()
        X_test = X_test.transpose(0, 3, 1, 2).copy()

        # Package data into a dictionary
        self.data = {
            'X_train': X_train, 'y_train': y_train,
            'X_val': X_val, 'y_val': y_val,
            'X_test': X_test, 'y_test': y_test,
        }

    #
    # Test1 - forward
    def test1(self):
        num_inputs = 2
        input_shape = (4, 5, 6)
        output_dim = 3

        input_size = num_inputs * np.prod(input_shape)
        weight_size = output_dim * np.prod(input_shape)

        x = np.linspace(-0.1, 0.5, num=input_size).reshape(num_inputs, *input_shape)
        w = np.linspace(-0.2, 0.3, num=weight_size).reshape(np.prod(input_shape), output_dim)
        b = np.linspace(-0.3, 0.1, num=output_dim)

        out, _ = fc_forward(x, w, b)
        correct_out = np.array([[1.49834967, 1.70660132, 1.91485297],
                                [3.25553199, 3.5141327, 3.77273342]])

        # Compare your output with ours. The error should be around 1e-9.
        print('Testing fc_forward function:')
        print('difference: ', rel_error(out, correct_out))

    #
    # Test2 - backprop
    def test2(self):
        np.random.seed(231)
        x = np.random.randn(10, 2, 3)
        w = np.random.randn(6, 5)
        b = np.random.randn(5)
        dout = np.random.randn(10, 5)

        dx_num = eval_numerical_gradient_array(lambda x: fc_forward(x, w, b)[0], x, dout)
        dw_num = eval_numerical_gradient_array(lambda w: fc_forward(x, w, b)[0], w, dout)
        db_num = eval_numerical_gradient_array(lambda b: fc_forward(x, w, b)[0], b, dout)

        _, cache = fc_forward(x, w, b)
        dx, dw, db = fc_backward(dout, cache)

        # The error should be around 1e-10
        print('Testing fc_backward function:')
        print('dx error: ', rel_error(dx_num, dx))
        print('dw error: ', rel_error(dw_num, dw))
        print('db error: ', rel_error(db_num, db))

    #
    # Test the relu_forward function
    def test3(self):
        x = np.linspace(-0.5, 0.5, num=12).reshape(3, 4)

        out, _ = relu_forward(x)
        correct_out = np.array([[0., 0., 0., 0., ],
                                [0., 0., 0.04545455, 0.13636364, ],
                                [0.22727273, 0.31818182, 0.40909091, 0.5, ]])

        # Compare your output with ours. The error should be around 5e-8
        print('Testing relu_forward function:')
        print('difference: ', rel_error(out, correct_out))

    #
    # ReLU layer: backward
    def test4(self):
        np.random.seed(231)
        x = np.random.randn(10, 10)
        dout = np.random.randn(*x.shape)

        dx_num = eval_numerical_gradient_array(lambda x: relu_forward(x)[0], x, dout)

        _, cache = relu_forward(x)
        dx = relu_backward(dout, cache)

        # The error should be around 3e-12
        print('Testing relu_backward function:')
        print('dx error: ', rel_error(dx_num, dx))

    #
    # Test: "Sandwich" layers
    def test5(self):

        from stats232a.layer_utils import fc_relu_forward, fc_relu_backward
        np.random.seed(231)
        x = np.random.randn(2, 3, 4)
        w = np.random.randn(12, 10)
        b = np.random.randn(10)
        dout = np.random.randn(2, 10)

        out, cache = fc_relu_forward(x, w, b)
        dx, dw, db = fc_relu_backward(dout, cache)

        dx_num = eval_numerical_gradient_array(lambda x: fc_relu_forward(x, w, b)[0], x, dout)
        dw_num = eval_numerical_gradient_array(lambda w: fc_relu_forward(x, w, b)[0], w, dout)
        db_num = eval_numerical_gradient_array(lambda b: fc_relu_forward(x, w, b)[0], b, dout)

        print('Testing affine_relu_forward:')
        print('dx error: ', rel_error(dx_num, dx))
        print('dw error: ', rel_error(dw_num, dw))
        print('db error: ', rel_error(db_num, db))

    #
    # Loss layers: Softmax
    def test6(self):
        np.random.seed(231)
        num_classes, num_inputs = 10, 50
        x = 0.001 * np.random.randn(num_inputs, num_classes)
        y = np.random.randint(num_classes, size=num_inputs)

        dx_num = eval_numerical_gradient(lambda x: softmax_loss(x, y)[0], x, verbose=False)
        loss, dx = softmax_loss(x, y)

        # Test softmax_loss function. Loss should be 2.3 and dx error should be 1e-8
        print('\nTesting softmax_loss:')
        print('loss: ', loss)
        print('dx error: ', rel_error(dx_num, dx))

    #
    # Test: Two-layer network
    def test7(self):
        np.random.seed(231)
        N, D, H, C = 3, 5, 50, 7
        X = np.random.randn(N, D)
        y = np.random.randint(C, size=N)

        std = 1e-3
        model = TwoLayerNet(input_dim=D, hidden_dim=H, num_classes=C)

        print('Testing test-time forward pass ... ')
        model.params['W1'] = np.linspace(-0.7, 0.3, num=D * H).reshape(D, H)
        model.params['b1'] = np.linspace(-0.1, 0.9, num=H)
        model.params['W2'] = np.linspace(-0.3, 0.4, num=H * C).reshape(H, C)
        model.params['b2'] = np.linspace(-0.9, 0.1, num=C)
        X = np.linspace(-5.5, 4.5, num=N * D).reshape(D, N).T
        scores = model.loss(X)
        correct_scores = np.asarray(
            [[11.53165108, 12.2917344, 13.05181771, 13.81190102, 14.57198434, 15.33206765, 16.09215096],
             [12.05769098, 12.74614105, 13.43459113, 14.1230412, 14.81149128, 15.49994135, 16.18839143],
             [12.58373087, 13.20054771, 13.81736455, 14.43418138, 15.05099822, 15.66781506, 16.2846319]])
        scores_diff = np.abs(scores - correct_scores).sum()
        assert scores_diff < 1e-6, 'Problem with test-time forward pass'

        print('Testing training loss (no regularization)')
        y = np.asarray([0, 5, 1])
        loss, grads = model.loss(X, y)
        correct_loss = 3.4702243556
        assert abs(loss - correct_loss) < 1e-10, 'Problem with training-time loss'

        model.reg = 1.0
        loss, grads = model.loss(X, y)
        correct_loss = 26.5948426952
        assert abs(loss - correct_loss) < 1e-10, 'Problem with regularization loss'

        for reg in [0.0, 0.7]:
            print('Running numeric gradient check with reg = ', reg)
            model.reg = 0
            loss, grads = model.loss(X, y)

            for name in sorted(grads):
                f = lambda _: model.loss(X, y)[0]
                grad_num = eval_numerical_gradient(f, model.params[name], verbose=False)
                print('%s relative error: %.2e' % (name, rel_error(grad_num, grads[name])))

    #
    # Test: Solver
    def test8(self):
        model = TwoLayerNet()

        ##############################################################################
        # TODO: Use a Solver instance to train a TwoLayerNet that achieves at least  #
        # 96% accuracy on the validation set.                                        #
        ##############################################################################
        solver = Solver(model, self.data,
                        update_rule='sgd',
                        optim_config={
                            'learning_rate': 1e-3,
                        },
                        lr_decay=0.95,
                        num_epochs=9, batch_size=200,
                        print_every=100)
        solver.train()
        ##############################################################################
        #                             END OF YOUR CODE                               #
        ##############################################################################

        # Run this cell to visualize training loss and train / val accuracy

        plt.subplot(2, 1, 1)
        plt.title('Training loss')
        plt.plot(solver.loss_history, 'o')
        plt.xlabel('Iteration')

        plt.subplot(2, 1, 2)
        plt.title('Accuracy')
        plt.plot(solver.train_acc_history, '-o', label='train')
        plt.plot(solver.val_acc_history, '-o', label='val')
        plt.plot([0.5] * len(solver.val_acc_history), 'k--')
        plt.xlabel('Epoch')
        plt.legend(loc='lower right')
        plt.gcf().set_size_inches(15, 12)
        plt.show()

    #
    # Test: Multiple Layers
    def test9(self):
        # TODO: Use a three-layer Net to overfit 50 training examples.
        # You will need to tweak the learning rate and initialization scale

        num_train = 50
        small_data = {
            'X_train': self.data['X_train'][:num_train],
            'y_train': self.data['y_train'][:num_train],
            'X_val': self.data['X_val'],
            'y_val': self.data['y_val'],
        }

        weight_scale = 1e-1
        learning_rate = 1e-4
        model = FullyConnectedNet([100, 100],
                                  weight_scale=weight_scale, dtype=np.float64)

        solver = Solver(model, small_data,
                        print_every=10, num_epochs=20, batch_size=25,
                        update_rule='sgd',
                        optim_config={
                            'learning_rate': learning_rate,
                        }
                        )
        solver.train()

        plt.plot(solver.loss_history, 'o')
        plt.title('Training loss history')
        plt.xlabel('Iteration')
        plt.ylabel('Training loss')
        plt.show()


    def test10(self):
        # TODO: Use a five-layer Net to overfit 50 training examples.
        # You will have to adjust the learning rate and weight initialization,

        num_train = 50
        small_data = {
            'X_train': self.data['X_train'][:num_train],
            'y_train': self.data['y_train'][:num_train],
            'X_val': self.data['X_val'],
            'y_val': self.data['y_val'],
        }

        learning_rate = 5e-4
        weight_scale = 1e-1
        model = FullyConnectedNet([100, 100, 100, 100],
                                  weight_scale=weight_scale, dtype=np.float64)
        solver = Solver(model, small_data,
                        print_every=10, num_epochs=20, batch_size=25,
                        update_rule='sgd',
                        optim_config={
                            'learning_rate': learning_rate,
                        }
                        )
        solver.train()

        plt.plot(solver.loss_history, 'o')
        plt.title('Training loss history')
        plt.xlabel('Iteration')
        plt.ylabel('Training loss')
        plt.show()

    #
    # SGD+Momentum test
    def test11(self):
        from stats232a.optim import sgd_momentum

        N, D = 4, 5
        w = np.linspace(-0.4, 0.6, num=N * D).reshape(N, D)
        dw = np.linspace(-0.6, 0.4, num=N * D).reshape(N, D)
        v = np.linspace(0.6, 0.9, num=N * D).reshape(N, D)

        config = {'learning_rate': 1e-3, 'velocity': v}
        next_w, _ = sgd_momentum(w, dw, config=config)

        expected_next_w = np.asarray([
            [0.1406, 0.20738947, 0.27417895, 0.34096842, 0.40775789],
            [0.47454737, 0.54133684, 0.60812632, 0.67491579, 0.74170526],
            [0.80849474, 0.87528421, 0.94207368, 1.00886316, 1.07565263],
            [1.14244211, 1.20923158, 1.27602105, 1.34281053, 1.4096]])
        expected_velocity = np.asarray([
            [0.5406, 0.55475789, 0.56891579, 0.58307368, 0.59723158],
            [0.61138947, 0.62554737, 0.63970526, 0.65386316, 0.66802105],
            [0.68217895, 0.69633684, 0.71049474, 0.72465263, 0.73881053],
            [0.75296842, 0.76712632, 0.78128421, 0.79544211, 0.8096]])

        print('next_w error: ', rel_error(next_w, expected_next_w))
        print('velocity error: ', rel_error(expected_velocity, config['velocity']))


    def test12(self):
        # six-layer network with both SGD and SGD+momentum. You should see the SGD+momentum update rule converge faster.
        num_train = 4000
        small_data = {
            'X_train': self.data['X_train'][:num_train],
            'y_train': self.data['y_train'][:num_train],
            'X_val': self.data['X_val'],
            'y_val': self.data['y_val'],
        }

        solvers = {}

        for update_rule in ['sgd', 'sgd_momentum']:
            print('running with ', update_rule)
            model = FullyConnectedNet([100, 100, 100, 100, 100], weight_scale=5e-2)

            solver = Solver(model, small_data,
                            num_epochs=5, batch_size=100,
                            update_rule=update_rule,
                            optim_config={
                                'learning_rate': 1e-2,
                            },
                            verbose=True)
            solvers[update_rule] = solver
            solver.train()
            print()

        plt.subplot(3, 1, 1)
        plt.title('Training loss')
        plt.xlabel('Iteration')

        plt.subplot(3, 1, 2)
        plt.title('Training accuracy')
        plt.xlabel('Epoch')

        plt.subplot(3, 1, 3)
        plt.title('Validation accuracy')
        plt.xlabel('Epoch')

        for update_rule, solver in list(solvers.items()):
            plt.subplot(3, 1, 1)
            plt.plot(solver.loss_history, 'o', label=update_rule)

            plt.subplot(3, 1, 2)
            plt.plot(solver.train_acc_history, '-o', label=update_rule)

            plt.subplot(3, 1, 3)
            plt.plot(solver.val_acc_history, '-o', label=update_rule)

        for i in [1, 2, 3]:
            plt.subplot(3, 1, i)
            plt.legend(loc='upper center', ncol=4)
        plt.gcf().set_size_inches(15, 15)
        plt.show()


    #
    # RMSProp
    def test13(self):
        # Test RMSProp implementation; you should see errors less than 1e-7
        from stats232a.optim import rmsprop

        N, D = 4, 5
        w = np.linspace(-0.4, 0.6, num=N * D).reshape(N, D)
        dw = np.linspace(-0.6, 0.4, num=N * D).reshape(N, D)
        cache = np.linspace(0.6, 0.9, num=N * D).reshape(N, D)

        config = {'learning_rate': 1e-2, 'cache': cache}
        next_w, _ = rmsprop(w, dw, config=config)

        expected_next_w = np.asarray([
            [-0.39223849, -0.34037513, -0.28849239, -0.23659121, -0.18467247],
            [-0.132737, -0.08078555, -0.02881884, 0.02316247, 0.07515774],
            [0.12716641, 0.17918792, 0.23122175, 0.28326742, 0.33532447],
            [0.38739248, 0.43947102, 0.49155973, 0.54365823, 0.59576619]])
        expected_cache = np.asarray([
            [0.5976, 0.6126277, 0.6277108, 0.64284931, 0.65804321],
            [0.67329252, 0.68859723, 0.70395734, 0.71937285, 0.73484377],
            [0.75037008, 0.7659518, 0.78158892, 0.79728144, 0.81302936],
            [0.82883269, 0.84469141, 0.86060554, 0.87657507, 0.8926]])

        print('next_w error: ', rel_error(expected_next_w, next_w))
        print('cache error: ', rel_error(expected_cache, config['cache']))


    #
    # Adam
    def test14(self):
        # Test Adam implementation; you should see errors around 1e-7 or less
        from stats232a.optim import adam

        N, D = 4, 5
        w = np.linspace(-0.4, 0.6, num=N * D).reshape(N, D)
        dw = np.linspace(-0.6, 0.4, num=N * D).reshape(N, D)
        m = np.linspace(0.6, 0.9, num=N * D).reshape(N, D)
        v = np.linspace(0.7, 0.5, num=N * D).reshape(N, D)

        config = {'learning_rate': 1e-2, 'm': m, 'v': v, 't': 5}
        next_w, _ = adam(w, dw, config=config)

        expected_next_w = np.asarray([
            [-0.40094747, -0.34836187, -0.29577703, -0.24319299, -0.19060977],
            [-0.1380274, -0.08544591, -0.03286534, 0.01971428, 0.0722929],
            [0.1248705, 0.17744702, 0.23002243, 0.28259667, 0.33516969],
            [0.38774145, 0.44031188, 0.49288093, 0.54544852, 0.59801459]])
        expected_v = np.asarray([
            [0.69966, 0.68908382, 0.67851319, 0.66794809, 0.65738853, ],
            [0.64683452, 0.63628604, 0.6257431, 0.61520571, 0.60467385, ],
            [0.59414753, 0.58362676, 0.57311152, 0.56260183, 0.55209767, ],
            [0.54159906, 0.53110598, 0.52061845, 0.51013645, 0.49966, ]])
        expected_m = np.asarray([
            [0.48, 0.49947368, 0.51894737, 0.53842105, 0.55789474],
            [0.57736842, 0.59684211, 0.61631579, 0.63578947, 0.65526316],
            [0.67473684, 0.69421053, 0.71368421, 0.73315789, 0.75263158],
            [0.77210526, 0.79157895, 0.81105263, 0.83052632, 0.85]])

        print('next_w error: ', rel_error(expected_next_w, next_w))
        print('v error: ', rel_error(expected_v, config['v']))
        print('m error: ', rel_error(expected_m, config['m']))



    #
    # Train with RMSProp and Adam
    def test15(self):
        num_train = 4000
        small_data = {
            'X_train': self.data['X_train'][:num_train],
            'y_train': self.data['y_train'][:num_train],
            'X_val': self.data['X_val'],
            'y_val': self.data['y_val'],
        }
        solvers = {}
        learning_rates = {'rmsprop': 1e-4, 'adam': 1e-3}
        for update_rule in ['adam', 'rmsprop']:
            print('running with ', update_rule)
            model = FullyConnectedNet([100, 100, 100, 100, 100], weight_scale=5e-2)

            solver = Solver(model, small_data,
                            num_epochs=5, batch_size=100,
                            update_rule=update_rule,
                            optim_config={
                                'learning_rate': learning_rates[update_rule]
                            },
                            verbose=True)
            solvers[update_rule] = solver
            solver.train()
            print()

        plt.subplot(3, 1, 1)
        plt.title('Training loss')
        plt.xlabel('Iteration')

        plt.subplot(3, 1, 2)
        plt.title('Training accuracy')
        plt.xlabel('Epoch')

        plt.subplot(3, 1, 3)
        plt.title('Validation accuracy')
        plt.xlabel('Epoch')

        for update_rule, solver in list(solvers.items()):
            plt.subplot(3, 1, 1)
            plt.plot(solver.loss_history, 'o', label=update_rule)

            plt.subplot(3, 1, 2)
            plt.plot(solver.train_acc_history, '-o', label=update_rule)

            plt.subplot(3, 1, 3)
            plt.plot(solver.val_acc_history, '-o', label=update_rule)

        for i in [1, 2, 3]:
            plt.subplot(3, 1, i)
            plt.legend(loc='upper center', ncol=4)
        plt.gcf().set_size_inches(15, 15)
        plt.show()


    #
    # Batch Normalization: Forward in training mode
    def test16(self):
        # Check the training-time forward pass by checking means and variances
        # of features both before and after batch normalization

        # Simulate the forward pass for a two-layer network
        N, D1, D2, D3 = 200, 50, 60, 3
        X = np.random.randn(N, D1)
        W1 = np.random.randn(D1, D2)
        W2 = np.random.randn(D2, D3)
        a = np.maximum(0, X.dot(W1)).dot(W2)

        print('Before batch normalization:')
        print('  means: ', a.mean(axis=0))
        print('  stds: ', a.std(axis=0))

        # Means should be close to zero and stds close to one
        print('After batch normalization (gamma=1, beta=0)')
        a_norm, _ = batchnorm_forward(a, np.ones(D3), np.zeros(D3), {'mode': 'train'})
        print('  mean: ', a_norm.mean(axis=0))
        print('  std: ', a_norm.std(axis=0))

        # Now means should be close to beta and stds close to gamma
        gamma = np.asarray([1.0, 2.0, 3.0])
        beta = np.asarray([11.0, 12.0, 13.0])
        a_norm, _ = batchnorm_forward(a, gamma, beta, {'mode': 'train'})
        print('After batch normalization (nontrivial gamma, beta)')
        print('  means: ', a_norm.mean(axis=0))
        print('  stds: ', a_norm.std(axis=0))


    #
    # Batch Normalization: Forward in test mode
    def test17(self):
        # Check the test-time forward pass by running the training-time
        # forward pass many times to warm up the running averages, and then
        # checking the means and variances of activations after a test-time
        # forward pass.

        N, D1, D2, D3 = 200, 50, 60, 3
        W1 = np.random.randn(D1, D2)
        W2 = np.random.randn(D2, D3)

        bn_param = {'mode': 'train'}
        gamma = np.ones(D3)
        beta = np.zeros(D3)
        for t in range(100):
            X = np.random.randn(N, D1)
            a = np.maximum(0, X.dot(W1)).dot(W2)
            batchnorm_forward(a, gamma, beta, bn_param)
        bn_param['mode'] = 'test'
        X = np.random.randn(N, D1)
        a = np.maximum(0, X.dot(W1)).dot(W2)
        a_norm, _ = batchnorm_forward(a, gamma, beta, bn_param)

        # Means should be close to zero and stds close to one, but will be
        # noisier than training-time forward passes.
        print('After batch normalization (test-time):')
        print('  means: ', a_norm.mean(axis=0))
        print('  stds: ', a_norm.std(axis=0))


    #
    # Batch Normalization: backward
    def test18(self):
        # Gradient check batchnorm backward pass

        N, D = 2, 3
        x = 5 * np.random.randn(N, D) + 12
        gamma = np.random.randn(D)
        beta = np.random.randn(D)
        dout = np.random.randn(N, D)

        bn_param = {'mode': 'train'}
        fx = lambda x: batchnorm_forward(x, gamma, beta, bn_param)[0]
        fg = lambda a: batchnorm_forward(x, gamma, beta, bn_param)[0]
        fb = lambda b: batchnorm_forward(x, gamma, beta, bn_param)[0]

        dx_num = eval_numerical_gradient_array(fx, x, dout)
        da_num = eval_numerical_gradient_array(fg, gamma, dout)
        db_num = eval_numerical_gradient_array(fb, beta, dout)
        dmean_num = np.sum(dx_num, axis=0) * N
        _, cache = batchnorm_forward(x, gamma, beta, bn_param)
        dx, dgamma, dbeta = batchnorm_backward(dout, cache)

        # print('dmean error: ', rel_error(dmean_num, dmean), dmean, dmean_num)
        print('dx error: ', rel_error(dx_num, dx))
        print('dgamma error: ', rel_error(da_num, dgamma))
        print('dbeta error: ', rel_error(db_num, dbeta))


    #
    # Batch Normalization: Fully Connected Net
    def test19(self):
        N, D, H1, H2, C = 2, 15, 20, 30, 10
        X = np.random.randn(N, D)
        y = np.random.randint(C, size=(N,))

        for reg in [0, 3.14]:
            print('Running check with reg = ', reg)
            model = FullyConnectedNet([H1, H2], input_dim=D, num_classes=C,
                                      reg=reg, weight_scale=5e-2, dtype=np.float64,
                                      use_batchnorm=True)
            loss, grads = model.loss(X, y)
            print('Initial loss: ', loss)
            grads.pop('dx')
            for name in sorted(grads):
                f = lambda _: model.loss(X, y)[0]
                grad_num = eval_numerical_gradient(f, model.params[name], verbose=False, h=1e-5)
                print('%s relative error: %.2e' % (name, rel_error(grad_num, grads[name])))
            if reg == 0:
                print()


    #
    # CIFAR-10
    def finalTest(self):
        """
        Load the CIFAR-10 dataset from disk and perform preprocessing to prepare
        it for classifiers. These are the same steps as we used for the SVM, but
        condensed to a single function.
        """
        # Load the raw CIFAR-10 data
        num_training = 49000
        num_validation = 1000
        num_test = 1000
        subtract_mean = True

        cifar10_dir = '/home/parallels/PycharmProjects/Courses/232A/project2/stats232a/datasets/cifar-10-batches-py'
        X_train, y_train, X_test, y_test = load_CIFAR10(cifar10_dir)

        # Subsample the data
        mask = list(range(num_training, num_training + num_validation))
        X_val = X_train[mask]
        y_val = y_train[mask]
        mask = list(range(num_training))
        X_train = X_train[mask]
        y_train = y_train[mask]
        mask = list(range(num_test))
        X_test = X_test[mask]
        y_test = y_test[mask]

        # Normalize the data: subtract the mean image
        if subtract_mean:
            mean_image = np.mean(X_train, axis=0)
            X_train -= mean_image
            X_val -= mean_image
            X_test -= mean_image

        # Transpose so that channels come first
        X_train = X_train.transpose(0, 3, 1, 2)
        X_val = X_val.transpose(0, 3, 1, 2)
        X_test = X_test.transpose(0, 3, 1, 2)

        # Package data into a dictionary
        data = {
            'X_train': X_train, 'y_train': y_train,
            'X_val': X_val, 'y_val': y_val,
            'X_test': X_test, 'y_test': y_test,
        }

        # Training
        weight_scale = 0
        learning_rate = 5e-4
        model = FullyConnectedNet([200, 200, 200, 200, 200], input_dim=3 * 32 * 32, reg=0.1,
                weight_scale=weight_scale, dtype=np.float64)

        solver = Solver(model, data,
                print_every=50, num_epochs=20, batch_size=256,
                update_rule='adam',
                optim_config={
                    'learning_rate': learning_rate
                },
                verbose=True)

        solver.train()

        plt.subplot(3, 1, 1)
        plt.title('Training loss')
        plt.xlabel('Iteration')

        plt.subplot(3, 1, 2)
        plt.title('Training accuracy')
        plt.xlabel('Epoch')

        plt.subplot(3, 1, 3)
        plt.title('Validation accuracy')
        plt.xlabel('Epoch')

        plt.subplot(3, 1, 1)
        plt.plot(solver.loss_history, 'o', label='Adam')

        plt.subplot(3, 1, 2)
        plt.plot(solver.train_acc_history, '-o', label='Adam')

        plt.subplot(3, 1, 3)
        plt.plot(solver.val_acc_history, '-o', label='Adam')

        plt.gcf().set_size_inches(15, 15)
        plt.show()


        best_model = solver.model
        y_test_pred = np.argmax(best_model.loss(data['X_test']), axis=1)
        y_val_pred = np.argmax(best_model.loss(data['X_val']), axis=1)
        print('Validation set accuracy: ', (y_val_pred == data['y_val']).mean())
        print('Test set accuracy: ', (y_test_pred == data['y_test']).mean())


#
# Implement test
#
test = Test()
test.finalTest()
