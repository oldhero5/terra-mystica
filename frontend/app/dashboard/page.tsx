'use client';

import { useAuth } from '@/hooks/use-auth';
import { ProfileForm } from '@/components/auth/profile-form';
import { ApiKeyManager } from '@/components/auth/api-key-manager';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useRouter } from 'next/navigation';
import { LogOut, User, Key, Upload, Map } from 'lucide-react';

export default function DashboardPage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    router.push('/auth/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Terra Mystica Dashboard
              </h1>
              <p className="text-muted-foreground">
                Welcome back, {user.full_name || user.username || user.email}
              </p>
            </div>
            <Button
              variant="outline"
              onClick={handleLogout}
              className="flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => router.push('/upload')}>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-primary/10 rounded-lg">
                    <Upload className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Upload Images</h3>
                    <p className="text-sm text-muted-foreground">Upload images to discover their locations</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="cursor-pointer hover:shadow-md transition-shadow opacity-50">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-accent/10 rounded-lg">
                    <Map className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-semibold">View Results</h3>
                    <p className="text-sm text-muted-foreground">Browse your analyzed images</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Welcome Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="w-5 h-5" />
                <span>Account Overview</span>
              </CardTitle>
              <CardDescription>
                Manage your Terra Mystica account settings and API access
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <h3 className="font-semibold">Account Status</h3>
                  <div className="flex items-center justify-center space-x-2 mt-2">
                    <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className="text-sm">{user.is_active ? 'Active' : 'Inactive'}</span>
                  </div>
                </div>
                
                <div className="text-center p-4 border rounded-lg">
                  <h3 className="font-semibold">Email Status</h3>
                  <div className="flex items-center justify-center space-x-2 mt-2">
                    <div className={`w-2 h-2 rounded-full ${user.is_verified ? 'bg-green-500' : 'bg-yellow-500'}`} />
                    <span className="text-sm">{user.is_verified ? 'Verified' : 'Pending'}</span>
                  </div>
                </div>
                
                <div className="text-center p-4 border rounded-lg">
                  <h3 className="font-semibold">API Access</h3>
                  <div className="flex items-center justify-center space-x-2 mt-2">
                    <Key className="w-4 h-4" />
                    <span className="text-sm">{user.api_key_name ? 'Active' : 'Not Set'}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Profile Management */}
          <ProfileForm />

          {/* API Key Management */}
          <ApiKeyManager />
        </div>
      </main>
    </div>
  );
}