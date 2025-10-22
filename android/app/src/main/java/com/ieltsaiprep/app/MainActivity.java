package com.ieltsaiprep.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.Plugin;

import java.util.ArrayList;

public class MainActivity extends BridgeActivity {
    
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Register any plugins here if needed
        // this.init(savedInstanceState, new ArrayList<Class<? extends Plugin>>() {{
        //     // Add plugins here
        // }});
    }
    
    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        
        // Handle deep links and QR code authentication
        Uri data = intent.getData();
        if (data != null) {
            // Handle QR code authentication redirect
            String scheme = data.getScheme();
            String host = data.getHost();
            String path = data.getPath();
            
            if ("ieltsaiprep".equals(scheme)) {
                // Handle custom scheme for QR code authentication
                // This will be processed by the web app
                getBridge().getActivity().runOnUiThread(() -> {
                    String url = "https://ieltsaiprep.com" + path;
                    if (data.getQuery() != null) {
                        url += "?" + data.getQuery();
                    }
                    
                    // Load the URL in the WebView
                    getBridge().getWebView().loadUrl(url);
                });
            }
        }
    }
}