import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


def linear_model(input_shape=(28, 28, 1)):
    inputs = tf.keras.Input(shape=input_shape)
    rescale = tf.keras.layers.Lambda(lambda x: x/255.0)(inputs)
    flatten = tf.keras.layers.Flatten()(rescale)
    outputs = tf.keras.layers.Dense(10, activation='softmax')(flatten)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    loss = tf.keras.losses.CategoricalCrossentropy()
    model.compile(loss=loss, optimizer='Adam', metrics=['accuracy'])
    return model


def create_adversarial_pattern(model, input_image, input_label):
    input_image = tf.cast(input_image, tf.float32)
    with tf.GradientTape() as tape:
        tape.watch(input_image)
        prediction = model(tf.expand_dims(input_image, axis=0))
        input_label = tf.reshape(input_label, (1, 10))
        loss = model.loss(input_label, prediction)

    gradient = tape.gradient(loss, input_image)
    signed_grad = tf.sign(gradient)
    return signed_grad

def create_adversarial_patterns(model, input_images, input_labels):
    input_images = tf.cast(input_images, tf.float32)
    with tf.GradientTape() as tape:
        tape.watch(input_images)
        predictions = model(input_images)
        input_labels = tf.reshape(input_labels, (-1, 10))
        losses = model.loss(input_labels, predictions)

    gradients = tape.gradient(losses, input_images)
    signed_grads = tf.sign(gradients)
    return signed_grads




if __name__ == '__main__':
    (train_data, train_labels), (test_data,
                                 test_labels) = tf.keras.datasets.mnist.load_data()

    train_labels = tf.one_hot(train_labels, depth=10, dtype=tf.float32)
    test_labels = tf.one_hot(test_labels, depth=10, dtype=tf.float32)

    mod = linear_model()
    mod.fit(train_data, train_labels, epochs=20,
            validation_data=(test_data, test_labels))
    mod.evaluate(test_data, test_labels)

    i = 1
    single_image = train_data[i].reshape(28, 28, 1)
    image_probs = mod.predict(tf.expand_dims(single_image, axis=0))
    single_label = tf.one_hot(0, image_probs.shape[-1])
    single_label = tf.reshape(single_label, (1, image_probs.shape[-1]))

    plt.imshow(single_image, cmap='gray')
    plt.show()

    noise = create_adversarial_pattern(mod, single_image, single_label)
    plt.imshow(noise*0.5+0.5)
    plt.show()

    epsilons = [0, 0.01, 0.05, 0.1, 0.15]
    for ind, elem in enumerate(epsilons):
        adv_x = single_image + elem*noise
        adv_x = tf.clip_by_value(adv_x, -1, 1)
        plt.imshow(adv_x)
        plt.show()

    noises = create_adversarial_patterns(mod,test_data,test_labels)
    epsilons = [0, 0.1, 0.2, 0.3, 0.4]
    for ind, elem in enumerate(epsilons):
        adv_xs = test_data + elem*noises
        # adv_xs = tf.clip_by_value(adv_xs, -1, 1)
        mod.evaluate(adv_xs,test_labels)