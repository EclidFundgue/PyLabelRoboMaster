import cv2
import numpy as np


class ONNXInference:
    def __init__(self, onnx_path, input_size=(640, 640), conf_thresh=0.5, nms_thresh=0.5):
        """
        初始化ONNX推理模型
        :param onnx_path: ONNX模型路径
        :param input_size: 模型输入尺寸 (width, height)
        :param conf_thresh: 置信度阈值
        :param nms_thresh: NMS阈值
        """
        # 初始化模型
        self.net = cv2.dnn.readNetFromONNX(onnx_path)
        self.input_width, self.input_height = input_size
        self.conf_threshold = conf_thresh
        self.nms_threshold = nms_thresh
        
        # 获取输出层名称
        self.output_names = self.net.getUnconnectedOutLayersNames()
        
        # 打印模型信息
        print(f"[INFO] 成功加载ONNX模型: {onnx_path}")
        print(f"[INFO] 输入尺寸: {input_size}")
        print(f"[INFO] 输出层: {self.output_names}")

    def preprocess(self, image):
        """
        图像预处理
        :param image: 输入图像 (BGR格式)
        :return: 预处理后的blob
        """
        # 转换为RGB格式（根据模型需求）
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 创建blob
        blob = cv2.dnn.blobFromImage(
            image=rgb_image,
            scalefactor=1.0/255.0,  # 归一化系数
            size=(self.input_width, self.input_height),
            mean=(0, 0, 0),         # 均值减除
            swapRB=False,           # 已转换为RGB，无需交换通道
            crop=False              # 不中心裁剪
        )
        return blob

    def inference(self, blob):
        """
        执行推理
        :param blob: 预处理后的blob
        :return: 模型输出
        """
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_names)
        return outputs

    def postprocess(self, outputs, orig_image):
        """
        后处理（示例为YOLO格式输出处理）
        :param outputs: 模型原始输出
        :param orig_image: 原始图像用于尺寸还原
        :return: 处理后的检测结果
        """
        # 获取原始图像尺寸
        orig_h, orig_w = orig_image.shape[:2]
        
        # 合并多个输出层的检测结果
        all_detections = []
        for output in outputs:
            # output shape: [batch_size, num_detections, 85]
            for detection in output[0]:
                scores = detection[4:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > self.conf_threshold:
                    # 还原坐标到原始图像尺寸
                    cx = detection[0] * orig_w
                    cy = detection[1] * orig_h
                    w = detection[2] * orig_w
                    h = detection[3] * orig_h
                    
                    # 转换为左上角坐标
                    x1 = int(cx - w/2)
                    y1 = int(cy - h/2)
                    x2 = int(cx + w/2)
                    y2 = int(cy + h/2)
                    
                    all_detections.append([x1, y1, x2, y2, confidence, class_id])

        # 应用NMS
        boxes = np.array([d[:4] for d in all_detections])
        scores = np.array([d[4] for d in all_detections])
        indices = cv2.dnn.NMSBoxes(
            bboxes=boxes.tolist(),
            scores=scores.tolist(),
            score_threshold=self.conf_threshold,
            nms_threshold=self.nms_threshold
        )

        # 最终结果
        final_results = []
        for i in indices:
            final_results.append(all_detections[i])
            
        return final_results

    def visualize(self, image, results):
        """
        结果可视化
        :param image: 原始图像
        :param results: 检测结果
        :return: 可视化后的图像
        """
        for res in results:
            x1, y1, x2, y2, conf, cls_id = res
            # 绘制矩形框
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 添加标签
            label = f"Class {cls_id}: {conf:.2f}"
            cv2.putText(image, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        return image

if __name__ == "__main__":
    # 示例用法
    model = ONNXInference("yolov5s.onnx")  # 替换为你的ONNX模型路径
    
    # 读取测试图像
    img = cv2.imread("test.jpg")
    
    # 预处理
    blob = model.preprocess(img)
    
    # 推理
    outputs = model.inference(blob)
    
    # 后处理
    results = model.postprocess(outputs, img)
    
    # 可视化
    vis_img = model.visualize(img.copy(), results)
    
    # 显示结果
    cv2.imshow("Result", vis_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()