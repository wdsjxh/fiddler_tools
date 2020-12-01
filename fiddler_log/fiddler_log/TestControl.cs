using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace fiddler_log
{
    public partial class TestControl : UserControl
    {
        public TestControl()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            MessageBox.Show("我被点击了!!!!");
        }

        private void TestControl_Load(object sender, EventArgs e)
        {

        }

        private void enable_CheckedChanged(object sender, EventArgs e)
        {

        }
    }
}
