'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';
import { RegisterRequest } from '@/types/auth';

interface RegisterFormProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

export function RegisterForm({ onSuccess, redirectTo = '/dashboard' }: RegisterFormProps) {
  const [formData, setFormData] = useState<RegisterRequest>({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirm_password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<RegisterRequest>>({});

  const { register } = useAuth();
  const { toast } = useToast();
  const router = useRouter();

  const validateForm = (): boolean => {
    const newErrors: Partial<RegisterRequest> = {};

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

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
    }

    // Confirm password validation
    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your password';
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field when user starts typing
    if (errors[name as keyof RegisterRequest]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const getPasswordStrength = (password: string): { strength: number; text: string; color: string } => {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) strength++;

    const strengthMap = [
      { text: 'Very Weak', color: 'text-red-500' },
      { text: 'Weak', color: 'text-orange-500' },
      { text: 'Fair', color: 'text-yellow-500' },
      { text: 'Good', color: 'text-blue-500' },
      { text: 'Strong', color: 'text-green-500' },
    ];

    return {
      strength,
      text: strengthMap[strength - 1]?.text || 'Very Weak',
      color: strengthMap[strength - 1]?.color || 'text-red-500',
    };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await register(formData);
      
      toast({
        title: "Account created successfully!",
        description: "Welcome to Terra Mystica. You are now logged in.",
      });

      if (onSuccess) {
        onSuccess();
      } else {
        router.push(redirectTo);
      }
    } catch (error) {
      toast({
        title: "Registration failed",
        description: error instanceof Error ? error.message : "An error occurred during registration",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          Create Account
        </CardTitle>
        <CardDescription>
          Join Terra Mystica to start geolocating your images
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email *</Label>
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
              placeholder="Choose a username (optional)"
              value={formData.username}
              onChange={handleChange}
              disabled={isLoading}
              className={errors.username ? 'border-destructive' : ''}
            />
            {errors.username && (
              <p className="text-sm text-destructive">{errors.username}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              name="full_name"
              type="text"
              placeholder="Enter your full name (optional)"
              value={formData.full_name}
              onChange={handleChange}
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password *</Label>
            <Input
              id="password"
              name="password"
              type="password"
              placeholder="Create a password"
              value={formData.password}
              onChange={handleChange}
              disabled={isLoading}
              className={errors.password ? 'border-destructive' : ''}
            />
            {formData.password && (
              <div className="flex items-center space-x-2">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      passwordStrength.strength <= 1 ? 'bg-red-500' :
                      passwordStrength.strength <= 2 ? 'bg-orange-500' :
                      passwordStrength.strength <= 3 ? 'bg-yellow-500' :
                      passwordStrength.strength <= 4 ? 'bg-blue-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${(passwordStrength.strength / 5) * 100}%` }}
                  />
                </div>
                <span className={`text-xs ${passwordStrength.color}`}>
                  {passwordStrength.text}
                </span>
              </div>
            )}
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm_password">Confirm Password *</Label>
            <Input
              id="confirm_password"
              name="confirm_password"
              type="password"
              placeholder="Confirm your password"
              value={formData.confirm_password}
              onChange={handleChange}
              disabled={isLoading}
              className={errors.confirm_password ? 'border-destructive' : ''}
            />
            {errors.confirm_password && (
              <p className="text-sm text-destructive">{errors.confirm_password}</p>
            )}
          </div>

          <Button
            type="submit"
            variant="aurora"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm">
          <span className="text-muted-foreground">Already have an account? </span>
          <button
            type="button"
            className="text-primary hover:text-primary/80 font-medium underline underline-offset-4"
            onClick={() => router.push('/auth/login')}
          >
            Sign in
          </button>
        </div>
      </CardContent>
    </Card>
  );
}