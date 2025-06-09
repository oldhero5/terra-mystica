'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';
import { User } from '@/types/auth';

interface ProfileFormData {
  username: string;
  full_name: string;
  email: string;
}

export function ProfileForm() {
  const { user, updateProfile } = useAuth();
  const { toast } = useToast();
  
  const [formData, setFormData] = useState<ProfileFormData>({
    username: '',
    full_name: '',
    email: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<ProfileFormData>>({});

  // Initialize form data when user data is available
  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        full_name: user.full_name || '',
        email: user.email,
      });
    }
  }, [user]);

  const validateForm = (): boolean => {
    const newErrors: Partial<ProfileFormData> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Username validation (optional but if provided, must be valid)
    if (formData.username && formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters long';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field when user starts typing
    if (errors[name as keyof ProfileFormData]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Only send fields that have changed
      const updatedFields: Partial<User> = {};
      
      if (formData.username !== (user?.username || '')) {
        updatedFields.username = formData.username || undefined;
      }
      
      if (formData.full_name !== (user?.full_name || '')) {
        updatedFields.full_name = formData.full_name || undefined;
      }
      
      if (formData.email !== user?.email) {
        updatedFields.email = formData.email;
      }

      if (Object.keys(updatedFields).length === 0) {
        toast({
          title: "No changes",
          description: "No changes were made to your profile.",
        });
        return;
      }

      await updateProfile(updatedFields);
      
      toast({
        title: "Profile updated",
        description: "Your profile has been successfully updated.",
      });
    } catch (error) {
      toast({
        title: "Update failed",
        description: error instanceof Error ? error.message : "An error occurred while updating your profile",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <Card className="w-full max-w-2xl">
        <CardContent className="p-6">
          <p className="text-center text-muted-foreground">Loading profile...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="text-2xl font-bold">Profile Settings</CardTitle>
        <CardDescription>
          Update your personal information and account settings
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                disabled={isLoading}
                className={errors.email ? 'border-destructive' : ''}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="Choose a username"
                value={formData.username}
                onChange={handleChange}
                disabled={isLoading}
                className={errors.username ? 'border-destructive' : ''}
              />
              {errors.username && (
                <p className="text-sm text-destructive">{errors.username}</p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              name="full_name"
              type="text"
              placeholder="Enter your full name"
              value={formData.full_name}
              onChange={handleChange}
              disabled={isLoading}
            />
          </div>

          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Account Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <Label className="text-muted-foreground">Account Status</Label>
                <div className="flex items-center space-x-2 mt-1">
                  <div className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span>{user.is_active ? 'Active' : 'Inactive'}</span>
                </div>
              </div>
              
              <div>
                <Label className="text-muted-foreground">Email Verified</Label>
                <div className="flex items-center space-x-2 mt-1">
                  <div className={`w-2 h-2 rounded-full ${user.is_verified ? 'bg-green-500' : 'bg-yellow-500'}`} />
                  <span>{user.is_verified ? 'Verified' : 'Pending'}</span>
                </div>
              </div>
              
              <div>
                <Label className="text-muted-foreground">Member Since</Label>
                <p className="mt-1">{new Date(user.created_at).toLocaleDateString()}</p>
              </div>
              
              <div>
                <Label className="text-muted-foreground">Last Updated</Label>
                <p className="mt-1">{new Date(user.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                // Reset form to original values
                if (user) {
                  setFormData({
                    username: user.username || '',
                    full_name: user.full_name || '',
                    email: user.email,
                  });
                  setErrors({});
                }
              }}
              disabled={isLoading}
            >
              Reset
            </Button>
            <Button
              type="submit"
              variant="aurora"
              disabled={isLoading}
            >
              {isLoading ? 'Updating...' : 'Update Profile'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}