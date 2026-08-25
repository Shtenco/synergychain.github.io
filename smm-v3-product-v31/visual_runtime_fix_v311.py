from pathlib import Path
import json, os
root=Path(os.environ.get('SMM_SRC','/tmp/smm-v311'))
main=root/'android/app/src/main/java/ai/sinergy/smm/MainActivity.java'
gradle=root/'android/app/build.gradle'
text=main.read_text()
if 'android.os.Build;' not in text:
    text=text.replace('import android.os.Bundle;','import android.os.Bundle;\nimport android.os.Build;')
if 'android.view.View;' not in text:
    text=text.replace('import android.util.Log;','import android.util.Log;\nimport android.view.View;')
needle='webView=new WebView(this); setContentView(webView);'
replacement='''webView=new WebView(this);\n        if (isEmulator()) {\n            webView.setLayerType(View.LAYER_TYPE_SOFTWARE, null);\n            Log.i(TAG,"EMULATOR_SOFTWARE_WEBVIEW");\n        }\n        setContentView(webView);'''
if needle in text:
    text=text.replace(needle,replacement)
if 'private static boolean isEmulator()' not in text:
    marker='    @Override public void onCreate(Bundle b){'
    helper='''    private static boolean isEmulator(){\n        String fp=Build.FINGERPRINT==null?"":Build.FINGERPRINT.toLowerCase();\n        String model=Build.MODEL==null?"":Build.MODEL.toLowerCase();\n        String product=Build.PRODUCT==null?"":Build.PRODUCT.toLowerCase();\n        return fp.startsWith("generic") || fp.contains("emulator") || fp.contains("sdk_gphone") || model.contains("emulator") || model.contains("android sdk built for") || product.contains("sdk_gphone");\n    }\n\n'''
    text=text.replace(marker,helper+marker)
main.write_text(text)
g=gradle.read_text().replace('versionCode 310','versionCode 311').replace("versionName '3.1.0'","versionName '3.1.1'")
gradle.write_text(g)
pm=root/'PRODUCT-MANIFEST.json'
if pm.exists():
    data=json.loads(pm.read_text())
    data['version']='3.1.1'; data['versionCode']=311
    data['visual_runtime_fix']='software WebView layer on emulator only; physical devices retain hardware acceleration'
    pm.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('V311_VISUAL_RUNTIME_PATCH_PASS')
