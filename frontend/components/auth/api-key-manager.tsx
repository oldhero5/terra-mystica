'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';
import { Copy, Eye, EyeOff, Key, Trash2 } from 'lucide-react';

export function ApiKeyManager() {
  const { user, generateApiKey, revokeApiKey } = useAuth();
  const { toast } = useToast();
  
  const [keyName, setKeyName] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRevoking, setIsRevoking] = useState(false);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [showKey, setShowKey] = useState(false);
  const [errors, setErrors] = useState<{ keyName?: string }>({});

  const validateKeyName = (): boolean => {
    const newErrors: { keyName?: string } = {};

    if (!keyName.trim()) {
      newErrors.keyName = 'API key name is required';
    } else if (keyName.trim().length < 3) {
      newErrors.keyName = 'API key name must be at least 3 characters long';
    } else if (keyName.trim().length > 100) {
      newErrors.keyName = 'API key name must be less than 100 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleGenerateKey = async () => {
    if (!validateKeyName()) {
      return;
    }

    setIsGenerating(true);

    try {
      const response = await generateApiKey(keyName.trim());
      setGeneratedKey(response.api_key);
      setKeyName('');
      setShowKey(true);
      
      toast({
        title: "API key generated",
        description: "Your new API key has been created successfully. Please copy it now as it won't be shown again.",
      });
    } catch (error) {
      toast({
        title: "Generation failed",
        description: error instanceof Error ? error.message : "Failed to generate API key",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRevokeKey = async () => {
    if (!user?.api_key_name) {
      return;
    }

    setIsRevoking(true);

    try {
      await revokeApiKey();
      setGeneratedKey(null);
      setShowKey(false);
      
      toast({
        title: "API key revoked",
        description: "Your API key has been successfully revoked.",
      });
    } catch (error) {
      toast({
        title: "Revocation failed",
        description: error instanceof Error ? error.message : "Failed to revoke API key",
        variant: "destructive",
      });
    } finally {
      setIsRevoking(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied to clipboard",
        description: "API key has been copied to your clipboard.",
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Failed to copy API key to clipboard.",
        variant: "destructive",
      });
    }
  };

  const maskKey = (key: string) => {
    if (key.length <= 8) return key;
    return `${key.substring(0, 8)}${'*'.repeat(key.length - 12)}${key.substring(key.length - 4)}`;
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Key className="w-5 h-5" />
          <span>API Key Management</span>
        </CardTitle>
        <CardDescription>
          Generate and manage your API keys for programmatic access to Terra Mystica
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current API Key Status */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Current API Key</h3>
          
          {user?.api_key_name ? (
            <div className="p-4 border rounded-lg space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-sm font-medium">Key Name</Label>
                  <p className="text-lg">{user.api_key_name}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRevokeKey}
                    disabled={isRevoking}
                    className="text-destructive hover:text-destructive"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    {isRevoking ? 'Revoking...' : 'Revoke'}
                  </Button>
                </div>
              </div>
              
              <div className="text-sm text-muted-foreground">
                <p>Status: <span className="text-green-600 font-medium">Active</span></p>
                <p className="mt-1">
                  Use this key in your API requests by including it in the Authorization header:
                </p>
                <code className="block mt-2 p-2 bg-muted rounded text-xs">
                  Authorization: Bearer YOUR_API_KEY
                </code>
              </div>
            </div>
          ) : (
            <div className="p-4 border border-dashed rounded-lg text-center">
              <Key className="w-8 h-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-muted-foreground">No API key generated</p>
              <p className="text-sm text-muted-foreground mt-1">
                Generate an API key to access Terra Mystica programmatically
              </p>
            </div>
          )}
        </div>

        {/* Generated Key Display */}
        {generatedKey && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-green-600">New API Key Generated</h3>
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-sm font-medium text-green-800">Your API Key</Label>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowKey(!showKey)}
                  className="text-green-700 hover:text-green-800"
                >
                  {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </Button>
              </div>
              
              <div className="flex items-center space-x-2">
                <code className="flex-1 p-2 bg-white border rounded text-sm break-all">
                  {showKey ? generatedKey : maskKey(generatedKey)}
                </code>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(generatedKey)}
                >
                  <Copy className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="text-sm text-green-700 bg-green-100 p-3 rounded">
                <p className="font-medium">⚠️ Important Security Notice</p>
                <p className="mt-1">
                  This is the only time you'll see this API key. Please copy and store it securely.
                  If you lose this key, you'll need to revoke it and generate a new one.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Generate New Key Form */}
        {!user?.api_key_name && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Generate New API Key</h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="keyName">API Key Name</Label>
                <Input
                  id="keyName"
                  placeholder="e.g., My Application Key"
                  value={keyName}
                  onChange={(e) => {
                    setKeyName(e.target.value);
                    if (errors.keyName) {
                      setErrors({ ...errors, keyName: undefined });
                    }
                  }}
                  disabled={isGenerating}
                  className={errors.keyName ? 'border-destructive' : ''}
                />
                {errors.keyName && (
                  <p className="text-sm text-destructive">{errors.keyName}</p>
                )}
                <p className="text-sm text-muted-foreground">
                  Choose a descriptive name to help you identify this key later
                </p>
              </div>

              <Button
                onClick={handleGenerateKey}
                disabled={isGenerating || !keyName.trim()}
                variant="aurora"
                className="w-full"
              >
                {isGenerating ? 'Generating...' : 'Generate API Key'}
              </Button>
            </div>
          </div>
        )}

        {/* API Documentation Link */}
        <div className="pt-6 border-t">
          <h3 className="text-lg font-semibold mb-2">API Documentation</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Learn how to use your API key to integrate Terra Mystica into your applications.
          </p>
          <Button variant="outline" asChild>
            <a href="/docs/api" target="_blank" rel="noopener noreferrer">
              View API Documentation
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}