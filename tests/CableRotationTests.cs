using System;
using System.Collections.Generic;
using VP.CSharpScript.Models.Atoms;
using VP.Services.Vps.Procedure.Atoms.Utility;

class CableRotationTests
{
    static int passed;
    static Dictionary<string, ScriptOutputItem> Outputs()
    {
        var d = new Dictionary<string, ScriptOutputItem>();
        foreach (string k in new[] { "Cable_Result", "Cable_Angle", "Cable_Direction", "Cable_OK" }) d[k] = new ScriptOutputItem();
        return d;
    }
    static void Check(bool ok, string name)
    {
        if (!ok) throw new Exception("FAIL: " + name);
        passed++;
        Console.WriteLine("PASS: " + name);
    }
    static Dictionary<string, object> Pose(double degrees)
    {
        double a = degrees * Math.PI / 180.0;
        double[] x = {-1, 1, 0, 0}, y = {0, 0, 1, -1};
        double[] rx = new double[4], ry = new double[4];
        for (int i = 0; i < 4; i++)
        {
            rx[i] = 100 + x[i] * Math.Cos(a) - y[i] * Math.Sin(a);
            ry[i] = 100 + x[i] * Math.Sin(a) + y[i] * Math.Cos(a);
        }
        return new Dictionary<string, object> {
            {"CenterX", rx}, {"CenterY", ry}, {"Labels", new[] {"brown", "yellow", "blue", "green"}},
            {"Scores", new double[] {.9, .9, .9, .9}}
        };
    }
    static void Main()
    {
        foreach (double angle in new double[] {0, -19.54, 19.54, -90, 90, 180})
        {
            var o = Outputs();
            int r = new ScriptClass().Do(Pose(angle), o);
            string expected = angle == 0 ? "无需旋转" : (angle < 0 || angle == 180 ? "顺时针" : "逆时针");
            Check(r == 0 && (bool)o["Cable_OK"].Value && Math.Abs((double)o["Cable_Angle"].Value - Math.Abs(angle)) < .001 && (string)o["Cable_Direction"].Value == expected, "pose " + angle);
        }
        var missing = Pose(0); missing.Remove("CenterX");
        var output = Outputs();
        Check(new ScriptClass().Do(missing, output) == 0 && !(bool)output["Cable_OK"].Value, "missing input is rejected");
        var incomplete = Pose(0); incomplete["Labels"] = new[] {"brown", "yellow", "blue"};
        output = Outputs();
        Check(new ScriptClass().Do(incomplete, output) == 0 && !(bool)output["Cable_OK"].Value, "missing color is rejected");
        var duplicate = Pose(0);
        duplicate["CenterX"] = new double[] {99,101,100,100,400};
        duplicate["CenterY"] = new double[] {100,100,101,99,400};
        duplicate["Labels"] = new[] {"brown","yellow","blue","green","brown"};
        duplicate["Scores"] = new double[] {.9,.9,.9,.9,.1};
        output = Outputs();
        Check(new ScriptClass().Do(duplicate, output) == 0 && (double)output["Cable_Angle"].Value == 0, "highest confidence color selected");
        var malformed = Pose(0); malformed["CenterX"] = new double[] {1};
        output = Outputs();
        Check(new ScriptClass().Do(malformed, output) == 1 && !(bool)output["Cable_OK"].Value, "malformed coordinate list reports exception");
        Console.WriteLine("Passed " + passed + " original-script math and error cases; no image inference tested.");
    }
}
