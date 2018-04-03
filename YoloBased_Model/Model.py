from keras.models import *
from keras.layers import *
from keras import backend as K
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.normalization import BatchNormalization

def YoloBasedModel(height, width, point_num, point_classes, phase='train'):
    assert phase in ['train','evaluate'], "Model phase must be train or evaluate!"

    input_tensor = Input((width, height, 3), name="input_tensor")
    base_model = darknet52(input_tensor, include_top=False)
    X = base_model.output
    X = DarkNet_ConvBlock(X, 1024, 1, strides=1, block_name='FinalConv')

    # FeatureMap上每个像素提供候选点的数量 * (可见性 x y+24)
    output_dims = point_num * (3+len(point_classes))
    # output
    X = Conv2D(output_dims, (1,1), activation='linear', name="output", use_bias=True)(X)
    FinalConvShape = K.int_shape(X)
    X = Reshape((FinalConvShape[1], FinalConvShape[2], point_num, 3+len(point_classes)))(X)

    if phase is 'train':
        ground_truth = Input((FinalConvShape[1], FinalConvShape[2], point_num, 3+len(point_classes)), name="ground_truth")
        # loss
        model_loss = Lambda(yolo_loss,output_shape=(1, ),name='yolo_loss',
            arguments={'point_num': point_num,
                       'point_classes': point_classes})([X, ground_truth])
        model = Model(inputs=input_tensor, outputs=model_loss)
    else:
        model = Model(inputs=input_tensor, outputs=X)


    model.compile(loss="mse", optimizer="adam")
    return model

def darknet52(image_input, include_top = True, class_num = 1000):
    # stage 1
    X = DarkNet_ConvBlock(image_input, 32, 3, block_name='Stage1')
    # stage 2
    X = DarkNet_ConvBlock(X, 64, 3, strides=2, padding='valid', block_name='Stage2')
    # stage 3 - res_block_1
    X = Darknet_Repeat_Residual_Block(X, [32,64], [1,3], block_name='Stage3_Res1', repeat_times=1)
    # stage 4
    X = DarkNet_ConvBlock(X, 128, 3, strides=2, padding='valid', block_name='Stage4')
    # stage 5 - res_block_2
    X = Darknet_Repeat_Residual_Block(X, [64,128], [1,3], block_name='Stage5_Res2', repeat_times=2)
    # stage 6
    X = DarkNet_ConvBlock(X, 256, 3, strides=2, padding='valid', block_name='Stage6')
    # stage 7 - res_block_3
    X = Darknet_Repeat_Residual_Block(X, [128,256], [1,3], block_name='Stage7_Res3', repeat_times=8)
    # stage 8
    X = DarkNet_ConvBlock(X, 512, 3, strides=2, padding='valid', block_name='Stage8')
    # stage 9 - res_block_4
    X = Darknet_Repeat_Residual_Block(X, [256,512], [1,3], block_name='Stage9_Res4', repeat_times=8)
    # stage 10
    X = DarkNet_ConvBlock(X, 1024, 3, strides=2, padding='valid', block_name='Stage10')
    # stage 11 - res_block_5
    X = Darknet_Repeat_Residual_Block(X, [512,1024], [1,3], block_name='Stage9_Res5', repeat_times=4)
    if include_top:
        X = GlobalAveragePooling2D()(X)
        X = Dense(class_num, activation='softmax', name='classify_output')(X)
    model = Model(inputs=image_input, outputs=X)
    return model

def DarkNet_ConvBlock(tensor, filter_num, kernel_size, strides=1, BN=True, padding='same', block_name=None):
    X = tensor
    X = Conv2D(filter_num, (kernel_size,kernel_size), strides=(strides,strides), padding=padding, name=block_name+'_Conv')(X)
    X = LeakyReLU(0.1, name=block_name+'_LRelu')(X)
    if BN:
        X = BatchNormalization(name=block_name+'_BN')(X)
    return X

def Darknet_Repeat_Residual_Block(tensor, filters, kernels, block_name=None, repeat_times=1):
    X = tensor
    for i in range(repeat_times):
        X_shortcut = X
        X = DarkNet_ConvBlock(X, filters[0], kernels[0], strides=1, block_name=block_name+'_{}_C1'.format(i))
        X = DarkNet_ConvBlock(X, filters[1], kernels[1], strides=1, block_name=block_name+'_{}_C2'.format(i))
        X = Concatenate(axis=-1)([X, X_shortcut])
    return X