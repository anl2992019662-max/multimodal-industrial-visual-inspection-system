using System;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Collections;
using System.Collections.Generic;
using VP.Services.Vps;
using VP.Models.Base.Specific.Procedure;
using VP.Services.Vps.Procedure.Atoms.Utility;
using VP.CSharpScript.Models.Atoms;
using VP.Windows.Infrastructure;
using System.Drawing;
using VP.Core;
using VP.Core.Geometry;
using VP.Algorithm.Wrapper;
using VP.Algorithm.Wrapper.Record;
using VP.Core.Image;

namespace VP.Services.Vps.Procedure.Atoms.Utility
{
    public class ScriptClass
    {
        public int Do(IDictionary<string, object> parameters, IDictionary<string, ScriptOutputItem> outputs)
        {
            int result = 0;
            ErrorMessage = string.Empty;

            try
            {
                IList centerX = GetList(parameters, "CenterX");
                IList centerY = GetList(parameters, "CenterY");
                IList labels = GetList(parameters, "Labels");
                IList scores = GetList(parameters, "Scores");

                if (centerX == null || centerY == null || labels == null || scores == null)
                {
                    SetError(outputs, "线缆检测数据为空，请复检");
                    return 0;
                }

                if (labels.Count == 0 || centerX.Count == 0 || centerY.Count == 0 || scores.Count == 0)
                {
                    SetError(outputs, "线缆未识别到目标，请复检");
                    return 0;
                }

                int zong = FindBest(labels, scores, "zong");
                int cheng = FindBest(labels, scores, "cheng");
                int lan = FindBest(labels, scores, "lan");
                int lv = FindBest(labels, scores, "lv");

                if (zong < 0 || cheng < 0 || lan < 0 || lv < 0)
                {
                    SetError(outputs, "线缆识别不完整，请复检");
                    return 0;
                }

                double zx = Convert.ToDouble(centerX[zong]);
                double zy = Convert.ToDouble(centerY[zong]);

                double cx = Convert.ToDouble(centerX[cheng]);
                double cy = Convert.ToDouble(centerY[cheng]);

                double bx = Convert.ToDouble(centerX[lan]);
                double by = Convert.ToDouble(centerY[lan]);

                double gx = Convert.ToDouble(centerX[lv]);
                double gy = Convert.ToDouble(centerY[lv]);

                /*
                 * 图像坐标系：
                 * X 向右为正
                 * Y 向下为正
                 *
                 * 目标：
                 * 1. zong-cheng 连线变成水平
                 * 2. lv 必须在 lan 上方
                 */

                // 当前 zong -> cheng 的图像角度，0°表示水平向右，90°表示向下
                double zcAngle = GetImageAngle(zx, zy, cx, cy);

                // 让 zong-cheng 变水平的最小旋转量
                // 正数 = 顺时针，负数 = 逆时针
                double candidate1 = NormalizeSignedAngle(0.0 - zcAngle);

                // 因为水平线 0° 和 180° 都是水平，所以还有一个补 180° 的候选
                double candidate2 = NormalizeSignedAngle(candidate1 + 180.0);

                // 计算四个线芯的大概中心，用来模拟旋转
                double centerCableX = (zx + cx + bx + gx) / 4.0;
                double centerCableY = (zy + cy + by + gy) / 4.0;

                bool candidate1GreenTop = IsGreenAboveBlueAfterRotate(
                    bx, by, gx, gy, centerCableX, centerCableY, candidate1);

                bool candidate2GreenTop = IsGreenAboveBlueAfterRotate(
                    bx, by, gx, gy, centerCableX, centerCableY, candidate2);

                double finalRotation = candidate1;

                if (candidate1GreenTop && !candidate2GreenTop)
                {
                    finalRotation = candidate1;
                }
                else if (!candidate1GreenTop && candidate2GreenTop)
                {
                    finalRotation = candidate2;
                }
                else
                {
                    // 如果两个都满足或两个都不满足，优先选角度绝对值较小的
                    if (Math.Abs(candidate2) < Math.Abs(candidate1))
                    {
                        finalRotation = candidate2;
                    }
                    else
                    {
                        finalRotation = candidate1;
                    }
                }

                double angle = Math.Abs(finalRotation);
                angle = Math.Round(angle, 2);

                string direction = "";

                if (angle < 0.01)
                {
                    direction = "无需旋转";
                }
                else if (finalRotation > 0)
                {
                    direction = "顺时针";
                }
                else
                {
                    direction = "逆时针";
                }

                string text = "";

                if (direction == "无需旋转")
                {
                    text = "线缆已处于标准姿态，旋转角度 0.00°";
                }
                else
                {
                    text = "线缆应" + direction + "旋转 " + angle.ToString("F2") + "°";
                }

                SetOutput(outputs, "Cable_Result", text);
                SetOutput(outputs, "Cable_Angle", angle);
                SetOutput(outputs, "Cable_Direction", direction);
                SetOutput(outputs, "Cable_OK", true);

                return result;
            }
            catch (Exception ex)
            {
                SetOutput(outputs, "Cable_Result", "线缆角度计算异常");
                SetOutput(outputs, "Cable_Angle", 0.0);
                SetOutput(outputs, "Cable_Direction", "异常");
                SetOutput(outputs, "Cable_OK", false);
                ErrorMessage = ex.Message;
                return 1;
            }
        }

        private IList GetList(IDictionary<string, object> parameters, string name)
        {
            if (!parameters.ContainsKey(name))
            {
                return null;
            }

            if (parameters[name] == null)
            {
                return null;
            }

            return parameters[name] as IList;
        }

        private int FindBest(IList labels, IList scores, string target)
        {
            int bestIndex = -1;
            double bestScore = -1.0;

            int count = labels.Count;

            if (scores.Count < count)
            {
                count = scores.Count;
            }

            for (int i = 0; i < count; i++)
            {
                string label = labels[i].ToString();
                double score = Convert.ToDouble(scores[i]);

                if (IsTargetLabel(label, target) && score > bestScore)
                {
                    bestIndex = i;
                    bestScore = score;
                }
            }

            return bestIndex;
        }

        private bool IsTargetLabel(string label, string target)
        {
            string s = label.Trim().ToLower();

            if (target == "zong")
            {
                return s == "zong" ||
                       s == "cong" ||
                       s == "brown" ||
                       s == "棕" ||
                       s == "棕色";
            }

            if (target == "cheng")
            {
                return s == "cheng" ||
                       s == "orange" ||
                       s == "橙" ||
                       s == "橙色" ||
                       s == "huang" ||
                       s == "yellow" ||
                       s == "黄" ||
                       s == "黄色" ||
                       s == "黄棕" ||
                       s == "黄棕色";
            }

            if (target == "lan")
            {
                return s == "lan" ||
                       s == "blue" ||
                       s == "蓝" ||
                       s == "蓝色";
            }

            if (target == "lv")
            {
                return s == "lv" ||
                       s == "green" ||
                       s == "绿" ||
                       s == "绿色";
            }

            return false;
        }

        // 图像坐标角度：0°向右，90°向下，180°向左，270°向上
        private double GetImageAngle(double x1, double y1, double x2, double y2)
        {
            double dx = x2 - x1;
            double dy = y2 - y1;

            double angle = Math.Atan2(dy, dx) * 180.0 / Math.PI;

            while (angle < 0.0)
            {
                angle += 360.0;
            }

            while (angle >= 360.0)
            {
                angle -= 360.0;
            }

            return angle;
        }

        // 归一化到 -180° ~ 180°
        // 正数表示顺时针，负数表示逆时针
        private double NormalizeSignedAngle(double angle)
        {
            while (angle > 180.0)
            {
                angle -= 360.0;
            }

            while (angle <= -180.0)
            {
                angle += 360.0;
            }

            return angle;
        }

        // 判断旋转后绿色 lv 是否在蓝色 lan 上面
        // 图像坐标里 Y 越小越靠上
        private bool IsGreenAboveBlueAfterRotate(
            double blueX, double blueY,
            double greenX, double greenY,
            double centerX, double centerY,
            double rotationDeg)
        {
            double blueRotY = RotatePointY(blueX, blueY, centerX, centerY, rotationDeg);
            double greenRotY = RotatePointY(greenX, greenY, centerX, centerY, rotationDeg);

            return greenRotY < blueRotY;
        }

        // 图像坐标系旋转，正角度 = 顺时针
        private double RotatePointY(double x, double y, double cx, double cy, double angleDeg)
        {
            double rad = angleDeg * Math.PI / 180.0;

            double dx = x - cx;
            double dy = y - cy;

            double sin = Math.Sin(rad);
            double cos = Math.Cos(rad);

            double newY = cy + dx * sin + dy * cos;

            return newY;
        }

        private void SetError(IDictionary<string, ScriptOutputItem> outputs, string message)
        {
            SetOutput(outputs, "Cable_Result", message);
            SetOutput(outputs, "Cable_Angle", 0.0);
            SetOutput(outputs, "Cable_Direction", "异常");
            SetOutput(outputs, "Cable_OK", false);
        }

        private void SetOutput(IDictionary<string, ScriptOutputItem> outputs, string name, object value)
        {
            if (outputs.ContainsKey(name))
            {
                outputs[name].Value = value;
            }
        }

        public string GetErrorMessage()
        {
            return ErrorMessage;
        }

        private string ErrorMessage = string.Empty;
    }
}